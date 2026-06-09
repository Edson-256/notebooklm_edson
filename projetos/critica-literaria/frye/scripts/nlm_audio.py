"""nlm_audio.py — wrappers finos para a CLI `nlm`, isolando o perfil via
NLM_PROFILE (env por subprocess — padrão de notebooklm_edson/PERFIS_NOTEBOOKLM.md,
funciona inclusive no `download`, que NÃO aceita --profile).

Cobre os comandos que o med_series_builder não tem (criar notebook, subir fonte,
apagar notebook) + áudio. Padrões de regex/polling herdados de
notebooklm_michalk/tools/med_series_builder/videos.py.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

UUID_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)

# status do artifact (nlm list artifacts) -> estado interno
STATUS_MAP = {
    "in_progress": "generating",
    "generating": "generating",
    "pending": "generating",
    "completed": "completed",
    "ready": "completed",
    "failed": "failed",
    "error": "failed",
}


class NlmError(RuntimeError):
    """Falha genérica de um comando nlm."""


class QuotaExhausted(RuntimeError):
    """Cota da conta esgotada (gRPC code 8 / RESOURCE_EXHAUSTED)."""


def _run(args: list[str], profile: str, timeout: int) -> subprocess.CompletedProcess:
    """Roda `nlm <args>` com NLM_PROFILE=<profile> isolado no processo."""
    env = os.environ.copy()
    env["NLM_PROFILE"] = profile
    try:
        return subprocess.run(
            ["nlm", *args], capture_output=True, text=True, timeout=timeout, env=env
        )
    except FileNotFoundError as e:
        raise NlmError(f"binário `nlm` não encontrado: {e}") from e
    except subprocess.TimeoutExpired as e:
        raise NlmError(f"timeout ({timeout}s) em: nlm {' '.join(args[:3])}…") from e


def _err(r: subprocess.CompletedProcess) -> str:
    return (r.stderr.strip() or r.stdout.strip())[:500]


def _is_quota_error(text: str) -> bool:
    t = text.lower()
    if "resource_exhausted" in t:
        return True
    if re.search(r"\bcode[:\s]+8\b", t):
        return True
    if "quota" in t and any(k in t for k in ("exhaust", "exceed", "limit", "esgot")):
        return True
    return False


def _extract_artifact_id(text: str) -> str | None:
    m = re.search(r"(?:artifact|audio)\s*(?:id)?[:\s]+([0-9a-f-]{20,})", text, re.I)
    if m:
        mm = UUID_RE.search(m.group(1))
        if mm:
            return mm.group(0)
    mm = UUID_RE.search(text)
    return mm.group(0) if mm else None


# ============================================================================
# AUTH
# ============================================================================

def check_auth(profile: str) -> None:
    # 0.7.2: `login --check` às vezes dá traceback; probe confiável = notebook list --json.
    r = _run(["notebook", "list", "--json"], profile, timeout=60)
    if r.returncode != 0:
        raise NlmError(
            f"perfil nlm '{profile}' não autenticado. Rode: nlm login -p {profile}\n{_err(r)}"
        )
    try:
        json.loads(r.stdout)
    except (ValueError, json.JSONDecodeError):
        raise NlmError(
            f"perfil nlm '{profile}' não retornou JSON válido (auth?). Rode: nlm login -p {profile}"
        )


# ============================================================================
# NOTEBOOK
# ============================================================================

def create_notebook(title: str, profile: str, timeout: int = 60) -> str:
    r = _run(["notebook", "create", title, "--json"], profile, timeout)
    if r.returncode != 0:
        raise NlmError(f"notebook create falhou: {_err(r)}")
    nb = _extract_artifact_id(r.stdout + "\n" + r.stderr)
    if not nb:
        raise NlmError(f"não consegui extrair id do notebook: {(r.stdout + r.stderr)[:300]}")
    return nb


def delete_notebook(notebook_id: str, profile: str, timeout: int = 60) -> None:
    r = _run(["notebook", "delete", notebook_id, "-y"], profile, timeout)
    if r.returncode != 0:
        raise NlmError(f"notebook delete falhou ({notebook_id}): {_err(r)}")


def list_notebooks(profile: str, timeout: int = 60) -> list[dict]:
    r = _run(["notebook", "list", "--json"], profile, timeout)
    if r.returncode != 0:
        raise NlmError(f"notebook list falhou: {_err(r)}")
    return json.loads(r.stdout)


# ============================================================================
# SOURCE
# ============================================================================

def add_source(notebook_id: str, file_path: str | Path, title: str, profile: str,
               wait_timeout: int = 300, timeout: int = 360) -> str | None:
    fp = Path(file_path)
    if not fp.exists():
        raise NlmError(f"fonte não existe: {fp}")
    r = _run(
        ["source", "add", notebook_id, "--file", str(fp), "--title", title,
         "--wait", "--wait-timeout", str(wait_timeout)],
        profile, timeout,
    )
    if r.returncode != 0:
        raise NlmError(f"source add falhou ({fp.name}): {_err(r)}")
    return _extract_artifact_id(r.stdout + "\n" + r.stderr)


# ============================================================================
# AUDIO
# ============================================================================

def create_audio(notebook_id: str, focus: str, profile: str, *,
                 fmt: str = "deep_dive", length: str = "long",
                 language: str = "pt-BR", source_ids: list[str] | None = None,
                 timeout: int = 300) -> str | None:
    args = ["audio", "create", notebook_id, "-f", fmt, "-l", length,
            "--language", language, "-y"]
    if focus:
        args += ["--focus", focus]
    if source_ids:
        args += ["-s", ",".join(s for s in source_ids if s)]
    r = _run(args, profile, timeout)
    combined = r.stdout + "\n" + r.stderr
    if _is_quota_error(combined):
        raise QuotaExhausted(combined[:500])
    if r.returncode != 0:
        raise NlmError(f"create audio falhou: {_err(r)}")
    return _extract_artifact_id(combined)


def list_artifacts(notebook_id: str, profile: str, timeout: int = 60) -> dict[str, dict]:
    # 0.7.2: `list artifacts` foi removido; usar `studio status <nb> --json`.
    r = _run(["studio", "status", notebook_id, "--json"], profile, timeout)
    if r.returncode != 0:
        raise NlmError(f"studio status falhou: {_err(r)}")
    arts = json.loads(r.stdout)
    if isinstance(arts, dict):
        arts = arts.get("artifacts", arts.get("value", []))
    return {a["id"]: a for a in arts if a.get("id")}


def download_audio(notebook_id: str, artifact_id: str | None, out_path: str | Path,
                   profile: str, timeout: int = 600) -> int:
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    args = ["download", "audio", notebook_id, "-o", str(out), "--no-progress"]
    if artifact_id:
        args += ["--id", artifact_id]
    r = _run(args, profile, timeout)  # download NÃO aceita --profile → NLM_PROFILE env
    if r.returncode != 0:
        raise NlmError(f"download audio falhou: {_err(r)}")
    if not out.exists() or out.stat().st_size == 0:
        raise NlmError("download não produziu arquivo")
    return out.stat().st_size
