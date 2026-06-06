#!/usr/bin/env python3
"""
Constrói 02_fontes_e_aulas.md a partir das listagens do dell-server
(/home/edson/dev/cof/data/) coletadas em /tmp/cof_dell/.

Diferente do 01_*.md (notebook NotebookLM), este inventário cobre o
projeto COF de DOWNLOAD direto do seminariodefilosofia.org rodando no
dell-server. As fontes aqui são arquivos em disco, não sources do NLM.

Hierarquia:
  Nível 1 = grupo (COF Original/Remasterizado/Extracurriculares)
  Nível 2 = aula/arquivo (número, título, data)
"""

import re
from pathlib import Path
from collections import defaultdict

LISTINGS = Path("/tmp/cof_dell")
ROOT = Path(__file__).parent
OUT = ROOT / "02_fontes_e_aulas.md"

REMOTE_HOST = "edson@100.71.148.95 (dell-server, Tailscale)"
REMOTE_PATH = "/home/edson/dev/cof/data/"

MONTHS_PT = ['janeiro','fevereiro','março','abril','maio','junho',
             'julho','agosto','setembro','outubro','novembro','dezembro']

def fmt_date(iso: str) -> str:
    y, m, d = iso.split('-')
    return f"{int(d)} de {MONTHS_PT[int(m)-1]} de {y}"


# ── Parsers ────────────────────────────────────────────────────────────

AULA_PAT = re.compile(r'^Aula_(\d{3,4})(?:-(.+?))?(?:\.(mp3|pdf|docx|m4a|txt))?$', re.IGNORECASE)


def parse_audio_filename(name: str):
    """Aula_001.mp3 → (1, None, None, 'mp3')"""
    m = AULA_PAT.match(name)
    if not m:
        return None
    num = int(m.group(1))
    rest = m.group(2)
    ext = m.group(3) or ''
    return num, rest, ext


def parse_trans_filename(name: str):
    """
    Aula_001-2009-03-14.pdf       → (1, '2009-03-14', None, 'pdf')
    Aula_000-Apresentacao_do_COF  → (0, None, 'Apresentacao do COF', 'pdf')
    Aula_006-2009-05-03_2.pdf     → (6, '2009-05-03', dup_marker, 'pdf')
    """
    m = AULA_PAT.match(name)
    if not m:
        return None
    num = int(m.group(1))
    rest = m.group(2) or ''
    ext = m.group(3) or ''
    date_iso = None
    title = None
    dup = ''
    dm = re.match(r'^(\d{4}-\d{2}-\d{2})(.*)$', rest)
    if dm:
        date_iso = dm.group(1)
        dup = dm.group(2).strip()
    elif rest:
        title = rest.replace('_', ' ').strip()
    return num, date_iso, title, ext, dup


# ── Construção ─────────────────────────────────────────────────────────

def load_lines(name: str):
    p = LISTINGS / name
    return [l.strip() for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


def build_aulas_section(title: str, listing_file: str, kind: str):
    """kind = 'audio' | 'trans'"""
    lines = load_lines(listing_file)
    out = [f"### {title} ({len(lines)} arquivos)"]
    if kind == 'audio':
        nums = []
        for name in sorted(lines):
            r = parse_audio_filename(name)
            if r:
                nums.append((r[0], name))
        nums.sort()
        if nums:
            faixa = f"{nums[0][0]:03d}–{nums[-1][0]:03d}"
            unique = sorted({n for n,_ in nums})
            out.append(f"- **Faixa numérica:** {faixa} ({len(unique)} aulas únicas)")
        out.append("")
        for n, name in nums:
            out.append(f"  - **Aula {n:03d}** — `{name}`")
    else:  # trans
        # agrupar por número (algumas aulas têm múltiplos arquivos)
        groups = defaultdict(list)
        for name in sorted(lines):
            r = parse_trans_filename(name)
            if r:
                num, date_iso, t, ext, dup = r
                groups[num].append((name, date_iso, t, ext, dup))
        if groups:
            ks = sorted(groups.keys())
            faixa = f"{ks[0]:03d}–{ks[-1]:03d}"
            out.append(f"- **Faixa numérica:** {faixa} ({len(ks)} aulas únicas)")
        out.append("")
        for k in sorted(groups.keys()):
            entries = groups[k]
            # data canônica: primeira com date_iso preenchida
            iso = next((e[1] for e in entries if e[1]), None)
            ttl = next((e[2] for e in entries if e[2]), None)
            label_parts = [f"**Aula {k:03d}**"]
            if iso:
                label_parts.append(fmt_date(iso))
            if ttl:
                label_parts.append(ttl)
            out.append("  - " + " — ".join(label_parts))
            for name, _, _, _, dup in entries:
                tag = f" [{dup}]" if dup else ""
                out.append(f"    - `{name}`{tag}")
    out.append("")
    return out


def build_livros_section(title: str, listing_file: str):
    lines = load_lines(listing_file)
    out = [f"### {title} ({len(lines)} arquivos)", ""]
    for name in sorted(lines):
        out.append(f"- {name}")
    out.append("")
    return out


def build_extra_section():
    full = (LISTINGS / "cof_extra_full.txt").read_text(encoding='utf-8')
    blocks = re.split(r'^### (.+)/$', full, flags=re.MULTILINE)
    # blocks: ['', dirname1, content1, dirname2, content2, ...]
    pairs = list(zip(blocks[1::2], blocks[2::2]))

    skip_dirs = {'audios', 'apostilas'}  # tratados separadamente
    out = ["## Extracurriculares", ""]
    out.append(f"Localização remota: `{REMOTE_PATH}extracurriculares/`. ")
    out.append("Cada pasta agrupa arquivos de uma palestra/conferência avulsa do Olavo "
               "fora do ciclo regular do COF.\n")

    palestras = []
    for dname, content in pairs:
        dpath = dname.strip()
        last = dpath.split('/')[-1]
        if last in skip_dirs:
            continue
        files = [l.strip() for l in content.splitlines() if l.strip() and not l.startswith('###')]
        palestras.append((last, files))

    palestras.sort(key=lambda x: x[0].lower())
    out.append(f"**Total de palestras/conferências:** {len(palestras)}\n")
    for name, files in palestras:
        out.append(f"### {name}")
        for f in sorted(files):
            out.append(f"- `{f}`")
        out.append("")
    return out


def main():
    out = []
    out.append("# Fontes do COF — disco do dell-server\n")
    out.append(f"**Host:** `{REMOTE_HOST}`  ")
    out.append(f"**Diretório raiz:** `{REMOTE_PATH}`  ")
    out.append("**Origem:** projeto `cof` (downloader Playwright do "
               "`seminariodefilosofia.org`).\n")
    out.append("Este inventário é **distinto** do `01_fontes_e_aulas.md` "
               "(que cataloga as 73 fontes do notebook NotebookLM). Aqui as "
               "fontes são **arquivos baixados em disco** no dell-server.\n")
    out.append("Hierarquia: nível 1 = grupo no diretório `data/`; nível 2 = "
               "arquivo individual (Aula NN, data e/ou título).\n")
    out.append("---\n")

    # COF Original
    out.append("## COF Original\n")
    out.append(f"Localização: `{REMOTE_PATH}COF Original/`\n")
    out += build_aulas_section("Áudios", "cof_orig_audios.txt", "audio")
    out += build_aulas_section("Transcrições", "cof_orig_trans.txt", "trans")
    out += build_livros_section("Livros", "cof_orig_livros.txt")

    # COF Remasterizado
    out.append("## COF Remasterizado\n")
    out.append(f"Localização: `{REMOTE_PATH}COF Remasterizado/`\n")
    out += build_aulas_section("Áudios", "cof_remast_audios.txt", "audio")
    out += build_aulas_section("Transcrições", "cof_remast_trans.txt", "trans")
    out += build_livros_section("Livros", "cof_remast_livros.txt")

    # Extracurriculares
    out += build_extra_section()

    # Resumo
    n_orig_audio = len(load_lines("cof_orig_audios.txt"))
    n_orig_trans = len(load_lines("cof_orig_trans.txt"))
    n_orig_livros = len(load_lines("cof_orig_livros.txt"))
    n_rem_audio = len(load_lines("cof_remast_audios.txt"))
    n_rem_trans = len(load_lines("cof_remast_trans.txt"))
    n_rem_livros = len(load_lines("cof_remast_livros.txt"))

    out.append("---\n")
    out.append("## Resumo\n")
    out.append(f"| Categoria              | Original | Remasterizado |")
    out.append(f"|------------------------|---------:|--------------:|")
    out.append(f"| Áudios (`Aula_NNN.mp3`)     | {n_orig_audio} | {n_rem_audio} |")
    out.append(f"| Transcrições (PDF/DOCX)     | {n_orig_trans} | {n_rem_trans} |")
    out.append(f"| Livros (PDF)                | {n_orig_livros} | {n_rem_livros} |")
    out.append("")
    total = (n_orig_audio + n_orig_trans + n_orig_livros
             + n_rem_audio + n_rem_trans + n_rem_livros)
    out.append(f"**Total geral em disco:** {total} arquivos "
               "(+ pastas de extracurriculares).\n")

    OUT.write_text("\n".join(out), encoding='utf-8')
    print(f"Gerado {OUT.name}")


if __name__ == "__main__":
    main()
