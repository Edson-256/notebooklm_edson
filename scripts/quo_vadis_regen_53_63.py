#!/usr/bin/env python3
"""Re-geração das cenas 53-63 do Quo Vadis no perfil NLM profissional.

Contexto: cenas 53-63 tinham conteúdo errado (bug local→global). O reset de
2026-05-29 removeu-as do metadata, regenerou no NLM, mas o --download nunca
foi executado. Os artifacts expiraram (11 dias). Este script cria um notebook
temporário na conta profissional (cota ociosa), gera os 11 áudios e baixa.

Subcomandos:
  --create-nb   Cria o notebook temporário e sobe as fontes P2.
  --generate    Cria os 11 artifacts de áudio (fire-and-forget com intervalo).
  --download    Baixa os áudios prontos + atualiza metadata.json + sync dell.
  --teardown    Apaga o notebook temporário na conta profissional.
  --status      Mostra o estado atual.

(Sem flags) → mostra --status.

Uso típico:
  python3 scripts/quo_vadis_regen_53_63.py --create-nb
  # aguardar fontes indexarem (~2 min)
  python3 scripts/quo_vadis_regen_53_63.py --generate
  # aguardar geração (~10-40 min); pode baixar em seguida
  python3 scripts/quo_vadis_regen_53_63.py --download
  # verificar resultado
  python3 scripts/quo_vadis_regen_53_63.py --teardown
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
import unicodedata
from datetime import datetime
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent                            # notebooklm_edson/
QV_DIR      = PROJECT_DIR / "projetos" / "literatura" / "quo_vadis"
PROMPTS_DIR = QV_DIR / "prompts_cenas"
AUDIOS_DIR  = QV_DIR / "audios"
CAPS_DIR    = QV_DIR / "QV-capitulos"
META_FILE   = AUDIOS_DIR / "metadata.json"
STATE_FILE  = QV_DIR / "_regen53_63_state.json"

# ── Configurações ──────────────────────────────────────────────────────────
PROFILE          = "profissional"
NB_TITLE         = "[QV-TEMP] Quo Vadis — Parte 2 (re-geração 53-63)"
SCENES_RANGE     = range(53, 64)                           # 53-63 inclusive
INTERVAL_CREATE  = 120                                     # segundos entre creates
POLL_INTERVAL    = 60
POLL_TIMEOUT     = 2400                                    # 40 min

# Fontes: toda a Parte 2 (cenas 53-63 estão em P2 C10-C16, mas carregamos toda P2)
P2_SOURCES = [f"QV-P2-C{i:02d}.md" for i in range(1, 20)]

# Informação de cada cena (derivada do manifest)
SCENES = [
    {"num": 53, "title": "A tentação oferecida por Chilon",
     "arquivo": "qv_053_tentacao_oferecida.m4a",
     "localizacao": "Parte 2, Capítulo 10 (cena 1/2)"},
    {"num": 54, "title": "As trezentas vergastadas e o perdão em nome de Cristo",
     "arquivo": "qv_054_trezentas_vergastadas.m4a",
     "localizacao": "Parte 2, Capítulo 10 (cena 2/2)"},
    {"num": 55, "title": "A súplica do tribuno na casa de Pedro",
     "arquivo": "qv_055_suplica_tribuno.m4a",
     "localizacao": "Parte 2, Capítulo 11 (cena 1/2)"},
    {"num": 56, "title": '"Continuas a amá-lo?" — a confissão aos pés do Apóstolo',
     "arquivo": "qv_056_continuas_ama.m4a",
     "localizacao": "Parte 2, Capítulo 11 (cena 2/2)"},
    {"num": 57, "title": 'O jardim dos mirtos e o "Onde tu estiveres, Caius"',
     "arquivo": "qv_057_jardim_mirtos.m4a",
     "localizacao": "Parte 2, Capítulo 12 (cena 1/1)"},
    {"num": 58, "title": "A libertação dos escravos pelo sinal do peixe",
     "arquivo": "qv_058_libertacao_escravos.m4a",
     "localizacao": "Parte 2, Capítulo 13 (cena 1/2)"},
    {"num": 59, "title": "O credo frio de Petrônio: pedras preciosas contra a eternidade",
     "arquivo": "qv_059_credo_frio.m4a",
     "localizacao": "Parte 2, Capítulo 13 (cena 2/2)"},
    {"num": 60, "title": "O olhar que se cruza: dois senhores do universo",
     "arquivo": "qv_060_olhar_cruza.m4a",
     "localizacao": "Parte 2, Capítulo 14 (cena 1/2)"},
    {"num": 61, "title": 'Roma banhada em fogo: "A cólera de Deus está suspensa sobre ela"',
     "arquivo": "qv_061_roma_banhada.m4a",
     "localizacao": "Parte 2, Capítulo 14 (cena 2/2)"},
    {"num": 62, "title": "O olhar mau de Popeia sobre o mar azul",
     "arquivo": "qv_062_olhar_mau.m4a",
     "localizacao": "Parte 2, Capítulo 15 (cena 1/1)"},
    {"num": 63, "title": '"Como é possível a terra conter ao mesmo tempo..."',
     "arquivo": "qv_063_como_possivel.m4a",
     "localizacao": "Parte 2, Capítulo 16 (cena 1/1)"},
]

UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
MAX_FOCUS_CHARS = 10000


# ── NLM helpers ────────────────────────────────────────────────────────────

def _nlm(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["NLM_PROFILE"] = PROFILE
    return subprocess.run(["nlm", *args], capture_output=True, text=True,
                          timeout=timeout, env=env)


def _extract_uuid(text: str) -> str | None:
    m = UUID_RE.search(text)
    return m.group(0) if m else None


def check_auth() -> None:
    r = _nlm(["notebook", "list", "--json"], timeout=60)
    if r.returncode != 0:
        raise SystemExit(f"Perfil '{PROFILE}' não autenticado. Rode: nlm login -p {PROFILE}\n{r.stderr[:300]}")
    try:
        json.loads(r.stdout)
    except ValueError:
        raise SystemExit(f"Perfil '{PROFILE}' não retornou JSON válido.")


def create_notebook(title: str) -> str:
    r = _nlm(["notebook", "create", title, "--json"])
    if r.returncode != 0:
        raise RuntimeError(f"notebook create falhou: {(r.stderr or r.stdout)[:300]}")
    nb = _extract_uuid(r.stdout + "\n" + r.stderr)
    if not nb:
        raise RuntimeError(f"não consegui extrair ID: {(r.stdout + r.stderr)[:300]}")
    return nb


def delete_notebook(nb_id: str) -> None:
    r = _nlm(["notebook", "delete", nb_id, "-y"])
    if r.returncode != 0:
        raise RuntimeError(f"notebook delete falhou: {(r.stderr or r.stdout)[:300]}")


def add_source(nb_id: str, file_path: Path, title: str) -> str | None:
    r = _nlm(
        ["source", "add", nb_id, "--file", str(file_path),
         "--title", title, "--wait", "--wait-timeout", "300"],
        timeout=360,
    )
    if r.returncode != 0:
        raise RuntimeError(f"source add falhou ({file_path.name}): {(r.stderr or r.stdout)[:200]}")
    return _extract_uuid(r.stdout + "\n" + r.stderr)


def create_audio(nb_id: str, focus: str) -> str | None:
    if len(focus) > MAX_FOCUS_CHARS:
        focus = focus[:MAX_FOCUS_CHARS - 3] + "..."
    r = _nlm(
        ["audio", "create", nb_id, "-f", "deep_dive", "-l", "default",
         "--language", "pt-BR", "-y", "--focus", focus],
        timeout=300,
    )
    combined = r.stdout + "\n" + r.stderr
    if "resource_exhausted" in combined.lower() or re.search(r"\bcode[:\s]+8\b", combined):
        raise RuntimeError(f"QUOTA ESGOTADA: {combined[:300]}")
    if r.returncode != 0:
        raise RuntimeError(f"create audio falhou: {(r.stderr or r.stdout)[:300]}")
    return _extract_uuid(combined)


def poll_artifact(nb_id: str, artifact_id: str) -> str:
    """Retorna 'completed', 'failed' ou 'timeout'."""
    deadline = time.monotonic() + POLL_TIMEOUT
    while time.monotonic() < deadline:
        r = _nlm(["studio", "status", nb_id, "--json"], timeout=60)
        if r.returncode == 0:
            try:
                arts = json.loads(r.stdout)
                if isinstance(arts, dict):
                    arts = arts.get("artifacts", arts.get("value", []))
                a = next((x for x in arts if x.get("id") == artifact_id), None)
                if a:
                    st = a.get("status", "").lower()
                    if st in ("completed", "ready"):
                        return "completed"
                    if st in ("failed", "error"):
                        return "failed"
            except (ValueError, KeyError):
                pass
        time.sleep(POLL_INTERVAL)
    return "timeout"


def download_audio(nb_id: str, artifact_id: str, out_path: Path) -> int:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    args = ["download", "audio", nb_id, "-o", str(out_path),
            "--no-progress", "--id", artifact_id]
    r = _nlm(args, timeout=600)
    if r.returncode != 0:
        raise RuntimeError(f"download falhou: {(r.stderr or r.stdout)[:200]}")
    if not out_path.exists() or out_path.stat().st_size == 0:
        raise RuntimeError("download não produziu arquivo")
    return out_path.stat().st_size


# ── State ──────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def init_state() -> dict:
    state = load_state()
    if not state:
        state = {
            "notebook_profissional": "",
            "created_at": datetime.now().isoformat(),
            "audios": {str(s["num"]): {"status": "pending", "artifact_id": ""}
                       for s in SCENES},
        }
        save_state(state)
    return state


# ── Metadata helpers ────────────────────────────────────────────────────────

def load_metadata() -> dict:
    return json.loads(META_FILE.read_text(encoding="utf-8"))


def save_metadata(data: dict) -> None:
    data["ultima_atualizacao"] = datetime.now().isoformat()
    META_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def mark_downloaded(scene: dict, out_path: Path, artifact_id: str) -> None:
    data = load_metadata()
    entry = {
        "arquivo": scene["arquivo"],
        "cena_numero": scene["num"],
        "titulo_completo": scene["title"],
        "localizacao": scene["localizacao"],
        "artifact_id": artifact_id,
        "data_geracao": datetime.now().isoformat(),
        "focus_topic": scene["title"],
        "prompt_type": "deep_dive",
        "source_ids": [],
        "status": "downloaded",
        "output_path": str(out_path),
        "tamanho_bytes": out_path.stat().st_size if out_path.exists() else 0,
    }
    # Inserir na posição correta (por cena_numero)
    audios = data["audios"]
    audios.append(entry)
    audios.sort(key=lambda a: a["cena_numero"])
    data["audios"] = audios
    data["total_cenas"] = len(audios)
    save_metadata(data)


# ── Subcomandos ────────────────────────────────────────────────────────────

def cmd_create_nb() -> None:
    print(f"\n=== CREATE-NB (perfil: {PROFILE}) ===")
    check_auth()
    state = init_state()

    if state.get("notebook_profissional"):
        print(f"Notebook já existe: {state['notebook_profissional']}")
        print("  Use --status para ver o estado ou --teardown para recriar.")
        return

    print(f"Criando notebook temporário: '{NB_TITLE}'…")
    nb = create_notebook(NB_TITLE)
    state["notebook_profissional"] = nb
    save_state(state)
    print(f"  ✓ notebook: {nb}")

    # Subir fontes P2
    sources_in_notebook = []
    for i, fname in enumerate(P2_SOURCES, 1):
        fp = CAPS_DIR / fname
        if not fp.exists():
            print(f"  ⚠ fonte não encontrada, pulando: {fname}")
            continue
        print(f"  [{i}/{len(P2_SOURCES)}] subindo {fname}…", end=" ", flush=True)
        try:
            sid = add_source(nb, fp, fname.replace(".md", ""))
            sources_in_notebook.append({"file": fname, "source_id": sid or ""})
            print(f"✓ ({sid[:8] if sid else 'sem id'})")
        except RuntimeError as e:
            print(f"ERRO: {e}")

    state["sources"] = sources_in_notebook
    save_state(state)
    print(f"\n  {len(sources_in_notebook)} fontes subidas. Aguarde ~2 min para indexação antes de --generate.\n")


def cmd_generate() -> None:
    print(f"\n=== GENERATE (perfil: {PROFILE}) ===")
    check_auth()
    state = init_state()
    nb = state.get("notebook_profissional")
    if not nb:
        raise SystemExit("Notebook não criado. Rode --create-nb primeiro.")

    print(f"Notebook: {nb}")
    audio_state = state.get("audios", {})
    pending = [s for s in SCENES if audio_state.get(str(s["num"]), {}).get("status") == "pending"]
    already  = [s for s in SCENES if audio_state.get(str(s["num"]), {}).get("status") != "pending"]

    if already:
        print(f"  Já criados/baixados: {[s['num'] for s in already]}")
    if not pending:
        print("  Todos já foram criados. Use --download para baixar.")
        return

    print(f"  A criar: {[s['num'] for s in pending]}")
    print()

    for i, scene in enumerate(pending, 1):
        prompt_prefix = f"{scene['num']:03d}_"
        prompt_file = next(
            (p for p in PROMPTS_DIR.iterdir() if p.name.startswith(prompt_prefix) and p.suffix == ".md"),
            None,
        )
        if not prompt_file:
            print(f"  [{i}/{len(pending)}] ERRO: prompt não encontrado para cena {scene['num']}")
            continue

        focus = prompt_file.read_text(encoding="utf-8").strip()
        print(f"  [{i}/{len(pending)}] Criando cena {scene['num']}: {scene['title'][:50]}…", end=" ", flush=True)
        try:
            artifact_id = create_audio(nb, focus)
            audio_state[str(scene["num"])] = {"status": "created", "artifact_id": artifact_id or ""}
            state["audios"] = audio_state
            save_state(state)
            print(f"✓ artifact={artifact_id[:8] if artifact_id else '?'}")
        except RuntimeError as e:
            print(f"ERRO: {e}")
            if "QUOTA" in str(e):
                print("  Cota esgotada. Pare e retome amanhã com --generate.")
                break

        if i < len(pending):
            print(f"     (aguardando {INTERVAL_CREATE}s…)", flush=True)
            time.sleep(INTERVAL_CREATE)

    created = [s for s in SCENES if state["audios"].get(str(s["num"]), {}).get("status") == "created"]
    print(f"\n  Criados: {len(created)}/11. Rode --download para baixar (poll + download automático).\n")


def cmd_download() -> None:
    print(f"\n=== DOWNLOAD (perfil: {PROFILE}) ===")
    check_auth()
    state = load_state()
    if not state:
        raise SystemExit("State não encontrado. Rode --create-nb e --generate primeiro.")
    nb = state.get("notebook_profissional")
    if not nb:
        raise SystemExit("Notebook não encontrado no state.")

    audio_state = state.get("audios", {})
    to_download = [
        s for s in SCENES
        if audio_state.get(str(s["num"]), {}).get("status") == "created"
        and audio_state.get(str(s["num"]), {}).get("artifact_id")
    ]

    if not to_download:
        print("  Nenhum audio com status 'created' + artifact_id. Verifique --status.")
        return

    print(f"  A baixar: {len(to_download)} áudios")
    done = 0

    for j, scene in enumerate(to_download, 1):
        art_id = audio_state[str(scene["num"])]["artifact_id"]
        out_path = AUDIOS_DIR / scene["arquivo"]
        print(f"\n  [{j}/{len(to_download)}] cena {scene['num']}: {scene['title'][:50]}")
        print(f"     artifact={art_id[:16]}… aguardando processamento…", flush=True)

        status = poll_artifact(nb, art_id)
        if status != "completed":
            print(f"     ⚠ poll: {status} — fica como 'created' para retomar.")
            continue

        ok = False
        for attempt, backoff in enumerate([0, 90, 240], 1):
            if backoff:
                print(f"     tentativa {attempt}, aguardando {backoff}s…", flush=True)
                time.sleep(backoff)
            try:
                sz = download_audio(nb, art_id, out_path)
                audio_state[str(scene["num"])]["status"] = "downloaded"
                state["audios"] = audio_state
                save_state(state)
                mark_downloaded(scene, out_path, art_id)
                print(f"     ✓ baixado {sz/1e6:.1f} MB → {out_path.name}")
                ok = True
                done += 1
                break
            except RuntimeError as e:
                print(f"     tentativa {attempt} falhou: {str(e)[:100]}")

        if not ok:
            print("     ⚠ não foi possível baixar. Retome com --download.")

    print(f"\n  Baixados: {done}/{len(to_download)}")
    if done > 0:
        _sync_to_dell()
    print()


def _sync_to_dell() -> None:
    sync_script = Path.home() / "dev/dell_server/podcast_system/sync/sync_to_dell.py"
    if not sync_script.exists():
        print("  sync_to_dell: script não encontrado, pulando.")
        return
    try:
        r = subprocess.run(
            [sys.executable, str(sync_script), "--project", "quo-vadis", "--apply", "--no-notify"],
            timeout=900, capture_output=True, text=True,
        )
        if r.returncode == 0:
            print("  ✓ sync → dell (quo-vadis)")
        else:
            print(f"  ⚠ sync_to_dell saiu com código {r.returncode}: {r.stderr[:150]}")
    except Exception as e:
        print(f"  ⚠ sync_to_dell falhou: {e}")


def cmd_teardown() -> None:
    print(f"\n=== TEARDOWN (perfil: {PROFILE}) ===")
    state = load_state()
    nb = state.get("notebook_profissional") if state else None
    if not nb:
        print("  Nenhum notebook profissional no state — nada a apagar.")
        return

    pending = [s for s in SCENES if state.get("audios", {}).get(str(s["num"]), {}).get("status") != "downloaded"]
    if pending:
        print(f"  ⚠ ATENÇÃO: {len(pending)} áudio(s) ainda NÃO baixados: {[s['num'] for s in pending]}")
        print("  Confirme com --teardown --force para apagar mesmo assim.")
        return

    check_auth()
    delete_notebook(nb)
    state["notebook_profissional"] = ""
    save_state(state)
    print(f"  ✓ notebook {nb} apagado. Pessoal mantido.")
    print("  State file mantido em _regen53_63_state.json para referência.\n")


def cmd_teardown_force() -> None:
    print(f"\n=== TEARDOWN FORÇADO (perfil: {PROFILE}) ===")
    state = load_state()
    nb = state.get("notebook_profissional") if state else None
    if not nb:
        print("  Nenhum notebook no state."); return
    check_auth()
    delete_notebook(nb)
    state["notebook_profissional"] = ""
    save_state(state)
    print(f"  ✓ notebook {nb} apagado (forçado).\n")


def cmd_status() -> None:
    state = load_state()
    if not state:
        print("\n  State não encontrado. Script não iniciado ainda.\n")
        return
    print(f"\n  notebook: {state.get('notebook_profissional') or '(não criado)'}")
    print(f"  criado em: {state.get('created_at','?')}")
    audio_state = state.get("audios", {})
    from collections import Counter
    c = Counter(v.get("status") for v in audio_state.values())
    print(f"  audios: {dict(c)}")
    print()
    for s in SCENES:
        st = audio_state.get(str(s["num"]), {})
        art = st.get("artifact_id", "")[:12]
        print(f"    {s['num']:3d} {st.get('status','?'):12s}  art={art}  {s['title'][:45]}")
    # Também mostra metadata.json
    try:
        data = load_metadata()
        meta_nums = {a["cena_numero"] for a in data["audios"]}
        in_meta = [n for n in range(53, 64) if n in meta_nums]
        print(f"\n  metadata.json: cenas 53-63 presentes = {in_meta}")
    except Exception:
        pass
    print()


# ── Main ───────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--create-nb",  action="store_true", help="Criar notebook temp na conta profissional")
    ap.add_argument("--generate",   action="store_true", help="Criar artifacts de áudio no NLM")
    ap.add_argument("--download",   action="store_true", help="Baixar áudios + atualizar metadata")
    ap.add_argument("--teardown",   action="store_true", help="Apagar notebook profissional")
    ap.add_argument("--force",      action="store_true", help="Forçar teardown mesmo com audios pendentes")
    ap.add_argument("--status",     action="store_true", help="Mostrar estado atual")
    args = ap.parse_args()

    if args.create_nb:
        cmd_create_nb()
    elif args.generate:
        cmd_generate()
    elif args.download:
        cmd_download()
    elif args.teardown:
        if args.force:
            cmd_teardown_force()
        else:
            cmd_teardown()
    else:
        cmd_status()


if __name__ == "__main__":
    main()
