"""notebooklm_edson-eev — cron_audio_daily.sh do COF v2 (dormente) com o fix do Aristóteles.

O wrapper real sai no bloco 'COF completo ... exit 0'. Para testar o caminho que
roda quando for reativado, o sandbox remove SÓ esse bloco numa cópia temporária.
"""
import shutil
import unittest

from tests._helpers import WrapperSandbox

WRAPPER = "projetos/filosofia/cof_v2/scripts/cron_audio_daily.sh"
DORMANT = ("# COF v2 CONCLUÍDO", 'saindo." >>"$LOG"\nexit 0\n')

SUMMARY = """  RESUMO DA SESSAO (0h40m)
  Itens tentados:    {t}
  Criados OK:        {ok}
  Falhas:            0"""


def make(strip=True):
    sb = WrapperSandbox(WRAPPER, ["scripts/nlm_quota_guard.sh"], strip=DORMANT if strip else None)
    venv_py = sb.repo / "projetos/filosofia/cof_v2/.venv/bin/python"
    venv_py.parent.mkdir(parents=True)
    shutil.copy(sb.stub_py, venv_py)
    return sb


class Dormente(unittest.TestCase):
    def test_wrapper_real_continua_desativado(self):
        sb = make(strip=False)
        try:
            p = sb.run()
            self.assertEqual(p.returncode, 0)
            self.assertEqual(sb.calls.read_text(), "", "não deve chamar o runner")
            self.assertFalse((sb.repo / ".nlm_quota_default_ts").exists())
            self.assertIn("cron desativado", sb.log_text("cof_cron_"))
        finally:
            sb.cleanup()


class Reativado(unittest.TestCase):
    def setUp(self):
        self.sb = make()
        self.quota = self.sb.repo / ".nlm_quota_default_ts"

    def tearDown(self):
        self.sb.cleanup()

    def test_criou_marca_cota(self):
        p = self.sb.run({"STUB_CREATE_OUT": SUMMARY.format(t=20, ok=20)})
        self.assertEqual(p.returncode, 0)
        self.assertTrue(self.quota.exists())
        calls = self.sb.calls.read_text()
        self.assertIn("--download", calls)
        self.assertIn("--max 20", calls)

    def test_zero_criados_nao_marca_cota(self):
        self.sb.run({"STUB_CREATE_OUT": SUMMARY.format(t=20, ok=0)})
        self.assertFalse(self.quota.exists())
        self.assertIn("NÃO marcando cota", self.sb.log_text("cof_cron_"))

    def test_auth_expirado_nao_marca_cota_e_notifica_auth(self):
        p = self.sb.run({"STUB_CREATE_OUT": "[08:00:01] ERRO: NLM NAO AUTENTICADO. Execute: nlm login",
                         "STUB_CREATE_RC": "1"})
        self.assertEqual(p.returncode, 1)
        self.assertFalse(self.quota.exists())
        self.assertIn("AUTH EXPIRADO", self.sb.notify_log.read_text())
        tg = [l for l in self.sb.calls.read_text().splitlines() if "tg_notify.py" in l]
        self.assertIn("--status auth_expired", tg[0])

    def test_auth_variante_client_authentication_error(self):
        self.sb.run({"STUB_DOWNLOAD_OUT": "notebooklm_tools.ClientAuthenticationError: token",
                     "STUB_CREATE_RC": "1"})
        self.assertIn("AUTH EXPIRADO", self.sb.notify_log.read_text())


if __name__ == "__main__":
    unittest.main()
