"""notebooklm_edson-f1t — Ben-Hur grava/baixa .m4a (nlm simulado rejeita outra extensão)."""
import json
import tempfile
import unittest
from pathlib import Path

from tests._helpers import FakeNlm, load_module

ART = "0000beef-1111-2222-3333-444444444444"  # fictício
SCENE = {"number": 7, "title": "A Corrida de Bigas", "location": "Antioquia"}


class BenHurM4a(unittest.TestCase):
    def setUp(self):
        self.r = load_module("projetos/literatura/ben-hur/ben_hur_runner.py", "ben_hur_runner")
        self.tmp = tempfile.TemporaryDirectory()
        self.r.BENHUR_DIR = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_filename_for_usa_m4a(self):
        name = self.r.filename_for(SCENE)
        self.assertTrue(name.startswith("bh_07_"))
        self.assertTrue(name.endswith(".m4a"))

    def test_criacao_e_download_ponta_a_ponta(self):
        rules = [
            {"match": ["create", "audio"], "stdout": f"Audio ID: {ART}\n"},
            {"match": ["studio", "status"],
             "stdout": json.dumps([{"id": ART, "status": "completed"}])},
            {"match": ["download", "audio"], "touch_output": True,
             "require_output_suffix": ".m4a"},
        ]
        with FakeNlm(rules):
            self.assertTrue(self.r.process_scene(SCENE))
            meta = json.loads((self.r.BENHUR_DIR / "audios/metadata.json").read_text())
            self.assertTrue(meta["audios"][0]["arquivo"].endswith(".m4a"))
            self.assertEqual(self.r.download_pending_audios(), 0)
        meta = json.loads((self.r.BENHUR_DIR / "audios/metadata.json").read_text())
        entry = meta["audios"][0]
        self.assertEqual(entry["status"], "downloaded")
        self.assertTrue(Path(entry["output_path"]).exists())


if __name__ == "__main__":
    unittest.main()
