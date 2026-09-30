"""Utilitários de teste: carregar runners por caminho e simular o CLI `nlm`.

O `nlm` real não existe fora do Mac do Edson. `FakeNlm` grava um executável
`nlm` num diretório temporário e o coloca à frente no PATH. O comportamento é
lido de um JSON (FAKE_NLM_SPEC) com regras por prefixo de subcomando:

    {"rules": [{"match": ["studio", "status"], "stdout": "[]", "rc": 0, "sleep": 0}],
     "calls_log": "/tmp/.../calls.jsonl"}

Cada chamada é registrada em `calls_log` (uma linha JSON com argv) para asserts.
Todos os dados são fictícios.
"""
from __future__ import annotations

import importlib.util
import json
import os
import stat
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

_FAKE_NLM_SRC = r'''#!/usr/bin/env python3
import json, os, sys, time
spec = json.load(open(os.environ["FAKE_NLM_SPEC"]))
argv = sys.argv[1:]
with open(spec["calls_log"], "a") as fh:
    fh.write(json.dumps(argv) + "\n")
for rule in spec.get("rules", []):
    m = rule["match"]
    if argv[:len(m)] == m:
        if rule.get("sleep"):
            time.sleep(rule["sleep"])
        if rule.get("touch_output"):
            for flag in ("-o", "--output"):
                if flag in argv:
                    open(argv[argv.index(flag) + 1], "wb").write(b"fake-audio")
        sys.stdout.write(rule.get("stdout", ""))
        sys.stderr.write(rule.get("stderr", ""))
        sys.exit(rule.get("rc", 0))
sys.stderr.write("fake nlm: comando sem regra: " + " ".join(argv))
sys.exit(2)
'''


def load_module(rel_path: str, name: str):
    path = REPO / rel_path
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeNlm:
    def __init__(self, rules: list[dict]):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.calls_log = d / "calls.jsonl"
        self.calls_log.touch()
        self.spec_path = d / "spec.json"
        self.set_rules(rules)
        exe = d / "nlm"
        exe.write_text(_FAKE_NLM_SRC.replace("#!/usr/bin/env python3", f"#!{sys.executable}", 1))
        exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
        self._old_path = os.environ.get("PATH", "")
        self._old_spec = os.environ.get("FAKE_NLM_SPEC")

    def set_rules(self, rules: list[dict]) -> None:
        self.spec_path.write_text(json.dumps({"rules": rules,
                                              "calls_log": str(self.calls_log)}))

    def calls(self) -> list[list[str]]:
        return [json.loads(l) for l in self.calls_log.read_text().splitlines() if l]

    def __enter__(self):
        os.environ["PATH"] = f"{self.tmp.name}{os.pathsep}{self._old_path}"
        os.environ["FAKE_NLM_SPEC"] = str(self.spec_path)
        return self

    def __exit__(self, *exc):
        os.environ["PATH"] = self._old_path
        if self._old_spec is None:
            os.environ.pop("FAKE_NLM_SPEC", None)
        else:
            os.environ["FAKE_NLM_SPEC"] = self._old_spec
        self.tmp.cleanup()
