"""notebooklm_edson-jvq — poll_status do COF v2 com timeout adequado (nlm simulado)."""
import json
import unittest

from tests._helpers import FakeNlm, load_module

runner = load_module("projetos/filosofia/cof_v2/scripts/06_audio_runner.py", "cof_v2_runner")

ART = "aaaaaaaa-1111-2222-3333-444444444444"  # fictício


class PollStatusTimeout(unittest.TestCase):
    def test_timeout_padrao_e_pelo_menos_90s(self):
        self.assertGreaterEqual(runner.POLL_STATUS_TIMEOUT, 90)

    def test_studio_lento_mas_dentro_do_timeout_retorna_status(self):
        # Studio "lento" (1s) com timeout de 3s: antes o teto fixo impedia ajustar.
        studio = [{"id": f"x{i}", "status": "completed"} for i in range(782)]
        studio.append({"id": ART, "status": "completed"})
        rules = [{"match": ["studio", "status"], "stdout": json.dumps(studio), "sleep": 1}]
        orig = runner.POLL_STATUS_TIMEOUT
        runner.POLL_STATUS_TIMEOUT = 3
        try:
            with FakeNlm(rules) as nlm:
                self.assertEqual(runner.poll_status(ART), "completed")
                self.assertEqual(nlm.calls()[0][:2], ["studio", "status"])
        finally:
            runner.POLL_STATUS_TIMEOUT = orig

    def test_timeout_estourado_vira_poll_error(self):
        rules = [{"match": ["studio", "status"], "stdout": "[]", "sleep": 3}]
        orig = runner.POLL_STATUS_TIMEOUT
        runner.POLL_STATUS_TIMEOUT = 1
        try:
            with FakeNlm(rules):
                self.assertEqual(runner.poll_status(ART), runner._POLL_ERROR)
        finally:
            runner.POLL_STATUS_TIMEOUT = orig

    def test_artifact_ausente_vira_poll_missing(self):
        with FakeNlm([{"match": ["studio", "status"], "stdout": "[]"}]):
            self.assertEqual(runner.poll_status(ART), runner._POLL_MISSING)

    def test_poll_status_usa_a_constante(self):
        seen = {}
        orig = runner.run_nlm
        def fake(args, timeout=120):
            seen["timeout"] = timeout
            raise runner.subprocess.TimeoutExpired(args, timeout)
        runner.run_nlm = fake
        try:
            self.assertEqual(runner.poll_status(ART), runner._POLL_ERROR)
        finally:
            runner.run_nlm = orig
        self.assertEqual(seen["timeout"], runner.POLL_STATUS_TIMEOUT)


if __name__ == "__main__":
    unittest.main()
