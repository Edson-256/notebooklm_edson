"""notebooklm_edson-xjgp — circuit breaker do HARVEST do Aristóteles (nlm simulado)."""
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FakeNlm, WrapperSandbox, load_module

NB = "nb000000-0000-0000-0000-000000000000"  # fictício


def art(i: int) -> str:
    return f"{i:08x}-aaaa-bbbb-cccc-dddddddddddd"


class HarvestBreaker(unittest.TestCase):
    def setUp(self):
        self.r = load_module("projetos/filosofia/aristoteles/scripts/07_audio_runner.py",
                             "aristoteles_runner")
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.r.AUDIO_META = d / "audio_metadata.json"
        self.r.AUDIOS_DIR = d / "audios"
        self.r.LOG_PATH = d / "audio_log.jsonl"
        self.lastrun = {}
        self.r._write_lastrun = lambda slug, reset=False, **f: self.lastrun.update(f)
        self.r._sync_to_dell = lambda slug, f: True
        # Timeouts reais (600s/130s) encurtados para 1s: o fake 'nlm' dorme 2s
        # nas regras de timeout, exercitando o caminho TimeoutExpired → rc 124.
        orig = self.r.run_nlm
        self.r.run_nlm = lambda args, timeout=120: orig(args, timeout=min(timeout, 1))

    def tearDown(self):
        self.tmp.cleanup()

    def _cenas(self, n):
        return [{"cena_id": f"obra/c{i:02d}", "audio_title": f"aristoteles_t{i:02d}",
                 "audio_filename": f"aristoteles_c{i:02d}.m4a"} for i in range(n)]

    def _meta_created(self, cenas):
        return {"audios": {c["cena_id"]: {"artifact_id": art(i), "status": "created"}
                           for i, c in enumerate(cenas)}}

    def _studio(self, cenas, titled=False):
        # CLI: título auto-gerado (não 'aristoteles_*'); UI: título canônico.
        return json.dumps([{"id": art(i), "status": "completed",
                            "title": c["audio_title"] if titled else f"Auto {i}"}
                           for i, c in enumerate(cenas)])

    def _dl_rule(self, i, kind):
        base = {"match": ["download", "audio", NB, "--id", art(i)]}
        if kind == "timeout":
            base["sleep"] = 2
        elif kind == "fail":
            base.update(rc=1, stderr="Error: Download failed for audio.")
        else:
            base["touch_output"] = True
        return base

    def test_tres_timeouts_consecutivos_abortam_o_harvest(self):
        cenas = self._cenas(10)
        meta = self._meta_created(cenas)
        rules = [{"match": ["studio", "status"], "stdout": self._studio(cenas)}]
        rules += [self._dl_rule(i, "timeout") for i in range(10)]
        with FakeNlm(rules) as nlm:
            rc = self.r.cmd_harvest({"cenas": cenas}, meta, {"notebook_id": NB}, dry_run=False)
            downloads = [c for c in nlm.calls() if c[:2] == ["download", "audio"]]
        self.assertEqual(rc, self.r.HARVEST_ABORTED_RC)
        self.assertEqual(len(downloads), 3, "deveria parar no 3º timeout")
        self.assertTrue(all(a["status"] == "created" for a in meta["audios"].values()))
        self.assertIn("HARVEST abortado", self.lastrun["harvest_aborted"])
        self.assertEqual(self.lastrun["dl_failed"], 3)
        log = [json.loads(l) for l in self.r.LOG_PATH.read_text().splitlines()]
        self.assertEqual([e["action"] for e in log if e["action"] == "harvest_aborted"],
                         ["harvest_aborted"])

    def test_falha_nao_timeout_zera_o_contador(self):
        cenas = self._cenas(6)
        meta = self._meta_created(cenas)
        kinds = ["timeout", "timeout", "fail", "timeout", "timeout", "ok"]
        rules = [{"match": ["studio", "status"], "stdout": self._studio(cenas)}]
        rules += [self._dl_rule(i, k) for i, k in enumerate(kinds)]
        with FakeNlm(rules) as nlm:
            rc = self.r.cmd_harvest({"cenas": cenas}, meta, {"notebook_id": NB}, dry_run=False)
            downloads = [c for c in nlm.calls() if c[:2] == ["download", "audio"]]
        self.assertEqual(rc, 0)
        self.assertEqual(len(downloads), 6)
        self.assertEqual(meta["audios"]["obra/c05"]["status"], "downloaded")
        self.assertEqual(self.lastrun["harvest_aborted"], "")

    def test_breaker_no_laco_de_titulos_ui_ainda_registra_created(self):
        cenas = self._cenas(5)
        meta = {"audios": {}}  # tudo pending; áudios gerados na UI com título canônico
        rules = [{"match": ["studio", "status"], "stdout": self._studio(cenas, titled=True)}]
        rules += [self._dl_rule(i, "timeout") for i in range(5)]
        with FakeNlm(rules) as nlm:
            rc = self.r.cmd_harvest({"cenas": cenas}, meta, {"notebook_id": NB}, dry_run=False)
            downloads = [c for c in nlm.calls() if c[:2] == ["download", "audio"]]
            polls = [c for c in nlm.calls() if c[:2] == ["studio", "status"]]
        self.assertEqual(rc, self.r.HARVEST_ABORTED_RC)
        self.assertEqual(len(downloads), 3)
        self.assertEqual(len(polls), 1, "com o breaker aberto não deve consultar o studio de novo")
        self.assertEqual({a["status"] for a in meta["audios"].values()}, {"created"})
        self.assertEqual(len(meta["audios"]), 5)

    def test_timeouts_de_consulta_ao_studio_tambem_contam(self):
        cenas = self._cenas(6)
        meta = self._meta_created(cenas)
        with FakeNlm([{"match": ["studio", "status"], "stdout": self._studio(cenas)}]) as nlm:
            # 1ª listagem responde; as consultas por item passam a travar.
            orig_poll = self.r.poll_status
            def slow_poll(nb, a):
                nlm.set_rules([{"match": ["studio", "status"], "stdout": "[]", "sleep": 2}])
                return orig_poll(nb, a)
            self.r.poll_status = slow_poll
            rc = self.r.cmd_harvest({"cenas": cenas}, meta, {"notebook_id": NB}, dry_run=False)
            polls = [c for c in nlm.calls() if c[:2] == ["studio", "status"]]
        self.assertEqual(rc, self.r.HARVEST_ABORTED_RC)
        self.assertEqual(len(polls), 1 + 3)


class WrapperSegueParaCreate(unittest.TestCase):
    """cron_audio.sh: harvest abortado (rc=3) → CREATE roda, cota marcada, notifica."""

    def setUp(self):
        self.sb = WrapperSandbox("projetos/filosofia/aristoteles/scripts/cron_audio.sh",
                                 ["scripts/nlm_quota_guard.sh"])

    def tearDown(self):
        self.sb.cleanup()

    def test_breaker_create_e_notificacao(self):
        p = self.sb.run({
            "STUB_HARVEST_OUT": "  ⛔ ERRO: HARVEST abortado — 3 timeouts consecutivos de nlm",
            "STUB_HARVEST_RC": "3",
            "STUB_CREATE_OUT": "Resultado: ok=20, adiados=0, failed=0",
        })
        calls = self.sb.calls.read_text()
        self.assertIn("--harvest", calls)
        self.assertIn("--create 20", calls)
        self.assertEqual(p.returncode, 3)
        self.assertTrue((self.sb.repo / ".nlm_quota_default_ts").exists(),
                        "cota deve ser marcada quando o CREATE cria algo")
        self.assertIn("HARVEST ABORTADO", self.sb.notify_log.read_text())
        self.assertIn("criados: 20", self.sb.notify_log.read_text())
        # Telegram: relatório 'ok' (com contagens), não 'failed'.
        tg = [l for l in calls.splitlines() if "tg_notify.py" in l]
        self.assertEqual(len(tg), 1)
        self.assertIn("--status ok", tg[0])



class TelegramMostraAborto(unittest.TestCase):
    def test_linha_do_breaker_no_relatorio_ok(self):
        tg = load_module("scripts/tg_notify.py", "tg_notify_t")
        msg = tg._format_state_report(
            "Aristóteles", "projetos/filosofia/aristoteles", "default", "ok",
            {"created": 20, "pending": 244, "downloaded": [],
             "harvest_aborted": "ERRO: HARVEST abortado — 3 timeouts consecutivos"})
        self.assertIn("⛔ ERRO: HARVEST abortado", msg)
        self.assertIn("Criados: 20", msg)


if __name__ == "__main__":
    unittest.main()
