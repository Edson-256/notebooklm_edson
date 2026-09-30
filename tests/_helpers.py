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


# ── Sandbox para os wrappers bash de cron ─────────────────────────────────
# Os wrappers têm caminhos absolutos do Mac (/Users/edsonmichalkiewicz/...) e
# chamam /opt/homebrew/bin/python3. Copiamos o wrapper (e os scripts que ele
# sourceia) para um HOME temporário, reescrevendo esses caminhos, e trocamos o
# python do runner por um stub bash que só registra argv e devolve a saída
# configurada via variáveis STUB_*.

MAC_HOME = "/Users/edsonmichalkiewicz"
MAC_PY = "/opt/homebrew/bin/python3"

_STUB_PY = r'''#!/bin/bash
echo "$*" >> "$STUB_CALLS"
case "$*" in
  *--harvest*)  printf '%b\n' "${STUB_HARVEST_OUT:-}"; exit "${STUB_HARVEST_RC:-0}";;
  *--download*) printf '%b\n' "${STUB_DOWNLOAD_OUT:-}"; exit "${STUB_DOWNLOAD_RC:-0}";;
  *--create*|*--max*) printf '%b\n' "${STUB_CREATE_OUT:-}"; exit "${STUB_CREATE_RC:-0}";;
  *) exit 0;;
esac
'''

_STUB_NOTIFIER = r'''#!/bin/bash
echo "$*" >> "$STUB_NOTIFY"
'''


class WrapperSandbox:
    def __init__(self, wrapper_rel: str, extra_rel: list[str] = (), strip: tuple[str, str] | None = None):
        """strip=(início, fim): remove do wrapper o trecho entre duas linhas-marco
        (inclusive) — usado para testar o COF com o bloco 'exit 0' dormente removido."""
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "home"
        self.repo = self.home / "dev" / "notebooklm_edson"
        self.stub_py = Path(self.tmp.name) / "stub_python"
        self.stub_py.write_text(_STUB_PY)
        self.stub_py.chmod(0o755)
        bindir = self.home / ".local" / "bin"
        bindir.mkdir(parents=True)
        notifier = bindir / "terminal-notifier"
        notifier.write_text(_STUB_NOTIFIER)
        notifier.chmod(0o755)
        self.calls = Path(self.tmp.name) / "calls.log"
        self.notify_log = Path(self.tmp.name) / "notify.log"
        self.calls.touch()
        self.notify_log.touch()
        for rel in [wrapper_rel, *extra_rel]:
            text = (REPO / rel).read_text()
            if rel == wrapper_rel and strip:
                a = text.index(strip[0])
                b = text.index(strip[1], a) + len(strip[1])
                text = text[:a] + text[b:]
            text = text.replace(MAC_HOME, str(self.home)).replace(MAC_PY, str(self.stub_py))
            dst = self.repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text)
            dst.chmod(0o755)
        self.wrapper = self.repo / wrapper_rel
        (self.repo / "logs").mkdir(exist_ok=True)

    def run(self, env: dict | None = None):
        import subprocess
        e = {"STUB_CALLS": str(self.calls), "STUB_NOTIFY": str(self.notify_log),
             "PATH": os.environ["PATH"]}
        e.update(env or {})
        return subprocess.run(["bash", str(self.wrapper)], env=e,
                              capture_output=True, text=True, timeout=60)

    def log_text(self, prefix: str) -> str:
        logs = sorted((self.repo / "logs").glob(f"{prefix}*.log"))
        return "\n".join(p.read_text() for p in logs)

    def cleanup(self):
        self.tmp.cleanup()
