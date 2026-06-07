#!/usr/bin/env python3
"""
Runner de audio (skill leitura-formativa) — best-of-breed do cof_v2.

STANDBY POR PADRAO: sem flag de acao, mostra apenas --status (NAO dispara nada).
Criacao exige --create N (ou --all). Download exige --download.

Principios (lições dos runners anteriores):
- Isolamento de conta SO via NLM_PROFILE (env var) em TODO subprocess; NUNCA 'nlm login switch'.
- 'nlm download audio' NAO aceita --profile -> NLM_PROFILE no env resolve.
- Rate-limit é ESTADO ('deferred'), nao falha -> re-tenta no proximo dia.
- poll_status 3 estados: status | _POLL_MISSING (sumiu do studio) | _POLL_ERROR (consulta falhou).
- Download com backoff [0,90,240]s ('completed' do NLM é prematuro).
- .m4a (nunca .mp3) + NFC nos filenames.
- Guard anti-colisao: aborta se NLM_PROFILE != perfil do projeto sem --force.
- Cota diaria por (perfil, data) com margem; rate-limit é a salvaguarda real (cota e compartilhada
  na conta com outros projetos -> este contador é por-projeto, informativo).

Uso:
    python3 audio_runner.py --project projetos/literatura/<slug> --status
    python3 audio_runner.py --project ... --dry-run
    python3 audio_runner.py --project ... --create 5
    python3 audio_runner.py --project ... --download
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time, unicodedata
from datetime import date, datetime
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:
    print("ERRO: requer Python 3.11+ (tomllib).", file=sys.stderr); sys.exit(1)

INTERVAL_SECONDS = 120
DOWNLOAD_BACKOFFS = [0, 90, 240]
CREATE_BACKOFFS = [0, 180, 300]
MAX_RETRIES = 3
MAX_FOCUS_CHARS = 10000

_RATE_LIMITED = object()
_POLL_MISSING = "__poll_missing__"
_POLL_ERROR = "__poll_error__"


def log(msg): print(f"[{datetime.now():%H:%M:%S}] {msg}")


def load_cfg(proj: Path) -> dict:
    cfg = tomllib.loads((proj / "projeto.toml").read_text(encoding="utf-8"))
    return cfg


def run_nlm(args, profile, timeout=180):
    env = os.environ.copy()
    env["NLM_PROFILE"] = profile
    return subprocess.run(["nlm"] + args, env=env, capture_output=True, text=True, timeout=timeout)


def check_auth(profile) -> bool:
    try:
        return run_nlm(["login", "--check", "--profile", profile], profile, timeout=30).returncode == 0
    except Exception as e:
        log(f"auth check erro: {e}"); return False


# ---- estado / cota / metadata ----
def quota_path(proj, cfg): return proj / cfg["paths"]["audios"] / "_daily_quota.json"

def quota_used_today(proj, cfg, profile) -> int:
    p = quota_path(proj, cfg)
    if not p.exists(): return 0
    return json.loads(p.read_text()).get(profile, {}).get(date.today().isoformat(), 0)

def quota_bump(proj, cfg, profile):
    p = quota_path(proj, cfg); p.parent.mkdir(parents=True, exist_ok=True)
    d = json.loads(p.read_text()) if p.exists() else {}
    today = date.today().isoformat()
    d.setdefault(profile, {})[today] = d.get(profile, {}).get(today, 0) + 1
    p.write_text(json.dumps(d, indent=2))

def meta_path(proj, cfg): return proj / cfg["paths"]["audios"] / "metadata.json"

def load_meta(proj, cfg) -> dict:
    p = meta_path(proj, cfg)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"audios": []}

def save_meta_entry(proj, cfg, entry):
    p = meta_path(proj, cfg); p.parent.mkdir(parents=True, exist_ok=True)
    data = load_meta(proj, cfg)
    by = {a["seq_global"]: a for a in data.get("audios", [])}
    by[entry["seq_global"]] = entry
    data = {"obra": cfg["obra"]["titulo"], "slug": cfg["obra"]["slug"],
            "notebook_id": cfg["notebooklm"]["notebook_id"],
            "atualizado": datetime.now().isoformat(),
            "audios": sorted(by.values(), key=lambda a: a["seq_global"])}
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---- cenas / prompts ----
def slug(s):
    s = unicodedata.normalize("NFKD", s.strip()).encode("ascii","ignore").decode("ascii")
    return re.sub(r"-{2,}","-", re.sub(r"[^\w\-]","", re.sub(r"[\s/\\]+","-", s))).strip("-")

def load_scenes(proj, cfg):
    man = json.loads((proj / cfg["paths"]["manifest"]).read_text(encoding="utf-8"))
    return man["cenas"], man.get("width", 2)

def scene_filename(c, width, ext):
    return f"{c['seq_global']:0{width}d}_cap-{c['cap']:0{width}d}_cena-{c['cena_local']:0{width}d}_{slug(c['titulo'])}.{ext}"

def load_prompt(proj, cfg, c, width):
    pdir = proj / cfg["paths"]["prompts"]
    prefix = f"prompt_{c['seq_global']:0{width}d}_"
    for f in pdir.iterdir():
        if f.name.startswith(prefix) and f.suffix == ".md":
            t = f.read_text(encoding="utf-8").strip()
            if len(t) > MAX_FOCUS_CHARS:
                log(f"AVISO truncamento: {f.name} ({len(t)} chars) -> revisar"); t = t[:MAX_FOCUS_CHARS-3] + "..."
            return t
    return None


# ---- NLM ops ----
def create_audio(cfg, profile, focus) -> object:
    nb = cfg["notebooklm"]["notebook_id"]
    cmd = ["audio", "create", nb, "--format", cfg["notebooklm"]["format"],
           "--language", cfg["notebooklm"]["language"], "--length", cfg["notebooklm"]["length"],
           "--focus", focus, "--profile", profile, "--confirm"]
    sids = cfg["notebooklm"].get("source_ids") or []
    if sids: cmd += ["--source-ids", ",".join(sids)]
    try:
        r = run_nlm(cmd, profile, timeout=240)
    except subprocess.TimeoutExpired:
        log("   timeout na criacao"); return None
    out = (r.stdout or "") + (r.stderr or "")
    low = out.lower()
    if "rate limit" in low or "code 8" in low or "wait a few minutes" in low or "quota" in low:
        return _RATE_LIMITED
    if r.returncode != 0:
        log(f"   nlm erro: {out.strip()[:300]}"); return None
    m = re.search(r"([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})", out)
    return m.group(1) if m else None

def poll_status(cfg, profile, artifact_id):
    try:
        r = run_nlm(["studio", "status", cfg["notebooklm"]["notebook_id"], "--json", "--profile", profile], profile, timeout=30)
        if r.returncode != 0: return _POLL_ERROR
        for a in json.loads(r.stdout):
            if a.get("id") == artifact_id: return a.get("status") or _POLL_MISSING
        return _POLL_MISSING
    except Exception:
        return _POLL_ERROR

def download_audio(cfg, profile, artifact_id, out_path: Path) -> bool:
    for i, wait in enumerate(DOWNLOAD_BACKOFFS, 1):
        if wait: log(f"   aguardando {wait}s (tentativa {i}/{len(DOWNLOAD_BACKOFFS)})..."); time.sleep(wait)
        try:
            r = run_nlm(["download", "audio", cfg["notebooklm"]["notebook_id"], "--id", artifact_id,
                         "--output", str(out_path), "--no-progress"], profile, timeout=300)
            if r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1_000_000:
                log(f"   download OK ({out_path.stat().st_size/1e6:.1f} MB)"); return True
        except Exception as e:
            log(f"   download erro: {e}")
    return False


# ---- acoes ----
def cmd_status(proj, cfg, scenes, width, profile):
    meta = {a["seq_global"]: a for a in load_meta(proj, cfg)["audios"]}
    from collections import Counter
    cnt = Counter(meta.get(c["seq_global"], {}).get("status", "pendente") for c in scenes)
    used = quota_used_today(proj, cfg, profile)
    cap = cfg["cota"]["por_dia"] - cfg["cota"].get("margem", 0)
    print(f"\n  {cfg['obra']['titulo']} — {len(scenes)} cenas | perfil {profile}")
    print(f"  cota hoje: {used}/{cap} (limite {cfg['cota']['por_dia']}, margem {cfg['cota'].get('margem',0)})")
    for st in ("downloaded","created","deferred","server_failed","lost_in_studio","pendente"):
        if cnt.get(st): print(f"    {st:16}: {cnt[st]}")
    print()

def pending_scenes(proj, cfg, scenes):
    meta = {a["seq_global"]: a for a in load_meta(proj, cfg)["audios"]}
    return [c for c in scenes if meta.get(c["seq_global"], {}).get("status") not in ("created","downloaded")]

def cmd_create(proj, cfg, scenes, width, profile, n, dry):
    queue = pending_scenes(proj, cfg, scenes)
    if n: queue = queue[:n]
    cap = cfg["cota"]["por_dia"] - cfg["cota"].get("margem", 0)
    used = quota_used_today(proj, cfg, profile)
    print(f"\n  Fila: {len(queue)} cenas | cota restante hoje: {max(0,cap-used)}")
    if dry:
        for c in queue: print(f"    cena {c['seq_global']:0{width}d}: {c['titulo']}  -> {scene_filename(c,width,'m4a')}")
        print("\n  [dry-run] nada disparado.\n"); return 0
    created = deferred = failed = 0
    for c in queue:
        if quota_used_today(proj, cfg, profile) >= cap:
            log(f"cota diaria atingida ({cap}) — parando; restantes ficam pendentes."); break
        focus = load_prompt(proj, cfg, c, width)
        if not focus: log(f"cena {c['seq_global']}: prompt ausente, pulando"); failed += 1; continue
        log(f"cena {c['seq_global']}: {c['titulo'][:50]}")
        art = None
        for attempt in range(1, MAX_RETRIES+1):
            art = create_audio(cfg, profile, focus)
            if art is _RATE_LIMITED:
                log("   rate-limited -> deferred"); break
            if art: break
            if attempt < MAX_RETRIES: time.sleep(CREATE_BACKOFFS[min(attempt-1, len(CREATE_BACKOFFS)-1)])
        entry = {"seq_global": c["seq_global"], "arquivo": scene_filename(c, width, "m4a"),
                 "titulo": c["titulo"], "cap": c["cap"], "notebook_profile": profile,
                 "data": datetime.now().isoformat()}
        if art is _RATE_LIMITED:
            entry["status"] = "deferred"; deferred += 1
        elif art:
            entry.update(status="created", artifact_id=art); quota_bump(proj, cfg, profile); created += 1
            log(f"   criado {art[:12]}...")
        else:
            entry["status"] = "server_failed"; failed += 1
        save_meta_entry(proj, cfg, entry)
        if c is not queue[-1] and art and art is not _RATE_LIMITED: time.sleep(INTERVAL_SECONDS)
    print(f"\n  criados={created} deferred={deferred} falhas={failed}\n")
    return 0

def cmd_download(proj, cfg, profile):
    pend = [a for a in load_meta(proj, cfg)["audios"] if a.get("status") == "created" and a.get("artifact_id")]
    if not pend: log("nada para baixar (status=created)."); return 0
    adir = proj / cfg["paths"]["audios"]; dl = proc = lost = err = 0
    for a in pend:
        st = poll_status(cfg, profile, a["artifact_id"])
        if st == "completed":
            out = adir / a["arquivo"]
            if download_audio(cfg, profile, a["artifact_id"], out):
                a.update(status="downloaded", output_path=str(out), tamanho_bytes=out.stat().st_size)
                save_meta_entry(proj, cfg, a); dl += 1
            else: err += 1
        elif st == "failed": a["status"]="server_failed"; save_meta_entry(proj,cfg,a); err+=1
        elif st == _POLL_MISSING: a["status"]="lost_in_studio"; save_meta_entry(proj,cfg,a); lost+=1
        elif st == _POLL_ERROR: err += 1
        else: proc += 1
    print(f"\n  baixados={dl} processando={proc} perdidos={lost} erros={err}\n")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Runner de audio leitura-formativa (standby por padrao)")
    ap.add_argument("--project", required=True)
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--create", type=int, metavar="N", help="disparar criacao de ate N cenas pendentes")
    ap.add_argument("--all", action="store_true", help="criar todas as pendentes (respeita cota)")
    ap.add_argument("--download", action="store_true")
    ap.add_argument("--force", action="store_true", help="ignora guard de perfil")
    args = ap.parse_args()

    proj = Path(args.project).expanduser()
    cfg = load_cfg(proj)
    profile = cfg["notebooklm"]["profile"]
    scenes, width = load_scenes(proj, cfg)

    # guard anti-colisao de perfil
    env_p = os.environ.get("NLM_PROFILE")
    if env_p and env_p != profile and not args.force:
        log(f"ABORTADO: NLM_PROFILE={env_p} != perfil do projeto '{profile}' (use --force)."); return 1

    # acoes que NAO tocam a conta
    if args.dry_run:
        return cmd_create(proj, cfg, scenes, width, profile, args.create or 0, dry=True)
    if not (args.create or args.all or args.download):
        return cmd_status(proj, cfg, scenes, width, profile)  # standby: so status

    if not check_auth(profile):
        log(f"ERRO: nlm nao autenticado no perfil {profile}. Rode: nlm login -p {profile}"); return 1
    if args.download:
        return cmd_download(proj, cfg, profile)
    return cmd_create(proj, cfg, scenes, width, profile, 0 if args.all else args.create, dry=False)


if __name__ == "__main__":
    sys.exit(main())
