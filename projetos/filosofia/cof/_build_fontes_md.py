#!/usr/bin/env python3
"""
Constrói 01_fontes_e_aulas.md a partir de _sources_list.json
e dos arquivos baixados em _raw/sources_content/.

Hierarquia:
  Nível 1 = fonte (nome no notebook)
  Nível 2 = aula (número, título quando houver, data)

Categorização das 73 fontes do COF:
  A) Compilações por ano (generated_text "Aulas Olavo - COF - YYYY[-x].md"):
     parsear "Aula NN" + data próxima.
  B) Compilações temáticas (2016, Apostilas, Artigos, Teoria do estado):
     listar fonte sem aulas internas (ou listar headings se existirem).
  C) PDFs avulsos "COF - Aula NNN.pdf": cada PDF é uma aula individual,
     agrupar todos sob "Aulas individuais (PDFs)".
  D) Textos do Olavo (livros, ensaios PDF/word_doc): grupo "Livros e ensaios".
  E) Materiais Unif_*: grupo "Material complementar (Unif_*)".
"""

import json, re
from pathlib import Path

ROOT = Path(__file__).parent
RAW = ROOT / "_raw" / "sources_content"
NOTEBOOK_ID = "12fec66e-81c2-4b94-b0d6-15d76a0b5e9b"

MONTHS = {
    'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marco': 3, 'abril': 4,
    'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
    'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12,
}
DATE_RE = re.compile(
    r'(\d{1,2})[ºo°]?\s+de\s+(janeiro|fevereiro|mar[çc]o|abril|maio|junho|julho|'
    r'agosto|setembro|outubro|novembro|dezembro)\s+de\s+(\d{4})',
    re.IGNORECASE,
)


def parse_aulas_in_compilation(filepath: Path):
    """Extrai aulas com seus números e datas de uma compilação ano-X.md."""
    text = filepath.read_text(encoding='utf-8', errors='replace')
    lines = text.splitlines()
    aulas = []
    for i, line in enumerate(lines):
        m = re.match(r'^Aula\s+(\d+)\s*$', line.strip())
        if not m:
            continue
        num = int(m.group(1))
        date_iso = None
        date_human = None
        for j in range(i, min(i + 15, len(lines))):
            dm = DATE_RE.search(lines[j])
            if dm:
                day = int(dm.group(1))
                month_name = dm.group(2).lower().replace('marco', 'março')
                month = MONTHS[month_name]
                year = int(dm.group(3))
                date_iso = f"{year:04d}-{month:02d}-{day:02d}"
                date_human = f"{day} de {month_name} de {year}"
                break
        aulas.append({
            'numero': num,
            'data_iso': date_iso,
            'data_human': date_human,
        })
    return aulas


def safe_filename(title: str) -> str:
    return title.replace('/', '_').replace(' ', '_')


def main():
    sources = json.loads((ROOT / "_sources_list.json").read_text(encoding='utf-8'))

    # Categorizar
    compilations_year = []   # 2009-a, ..., 2015 (generated_text com "Aulas Olavo - COF - YYYY")
    compilations_theme = []  # 2016, Apostilas, Artigos, Teoria do estado
    pdfs_aula = []           # "COF - Aula NNN.pdf"
    livros_ensaios = []      # outros word_doc/PDF
    unif = []                # "Unif_*"

    for s in sources:
        title = s['title']
        if title.startswith('Unif_'):
            unif.append(s)
        elif re.match(r'^COF - Aula \d+\.pdf$', title):
            pdfs_aula.append(s)
        elif title.startswith('Aulas Olavo - COF - '):
            stem = title[len('Aulas Olavo - COF - '):].rsplit('.md', 1)[0]
            if re.match(r'^\d{4}(-[ab])?$', stem):
                compilations_year.append(s)
            else:
                compilations_theme.append(s)
        else:
            livros_ensaios.append(s)

    # Ordenar
    def year_key(s):
        stem = s['title'][len('Aulas Olavo - COF - '):].rsplit('.md', 1)[0]
        m = re.match(r'^(\d{4})(?:-([ab]))?$', stem)
        return (int(m.group(1)), m.group(2) or '')
    compilations_year.sort(key=year_key)

    pdfs_aula.sort(key=lambda s: int(re.search(r'Aula\s+(\d+)', s['title']).group(1)))
    livros_ensaios.sort(key=lambda s: s['title'].lower())
    unif.sort(key=lambda s: s['title'].lower())
    compilations_theme.sort(key=lambda s: s['title'].lower())

    # Construir markdown
    out = []
    out.append("# Fontes do COF — notebook pessoal\n")
    out.append(f"**Notebook ID:** `{NOTEBOOK_ID}`  ")
    out.append(f"**Conta:** `default` (edson.michalkiewicz@gmail.com)  ")
    out.append(f"**Total de fontes:** {len(sources)}\n")
    out.append("Hierarquia: nível 1 = fonte (como aparece no notebook); ")
    out.append("nível 2 = aula (número e data, quando aplicável).\n")
    out.append("---\n")

    # A) Compilações por ano
    out.append("## Compilações de aulas por ano\n")
    out.append("Cada arquivo agrupa as aulas transcritas de um período. ")
    out.append("Datas extraídas automaticamente do conteúdo (linha logo após `Aula NN`).\n")

    for s in compilations_year:
        title = s['title']
        sid = s['id']
        local_file = RAW / safe_filename(title)
        out.append(f"### {title}")
        out.append(f"- **source_id:** `{sid}`")
        if local_file.exists():
            aulas = parse_aulas_in_compilation(local_file)
            out.append(f"- **Aulas detectadas:** {len(aulas)}")
            if aulas:
                nums = [a['numero'] for a in aulas]
                out.append(f"- **Faixa numérica:** {min(nums)}–{max(nums)}")
            out.append("")
            for a in aulas:
                num = a['numero']
                date_h = a['data_human'] or '*data não detectada*'
                out.append(f"  - **Aula {num:03d}** — {date_h}")
        else:
            out.append("- *(conteúdo não baixado)*")
        out.append("")

    # B) Compilações temáticas (sem aulas numeradas internas detectadas)
    out.append("## Compilações temáticas (sem numeração de aula interna)\n")
    for s in compilations_theme:
        out.append(f"### {s['title']}")
        out.append(f"- **source_id:** `{s['id']}`")
        local_file = RAW / safe_filename(s['title'])
        if local_file.exists():
            aulas = parse_aulas_in_compilation(local_file)
            if aulas:
                out.append(f"- **Aulas detectadas:** {len(aulas)}")
                for a in aulas:
                    num = a['numero']
                    date_h = a['data_human'] or '*data não detectada*'
                    out.append(f"  - **Aula {num:03d}** — {date_h}")
            else:
                out.append("- *Sem padrão `Aula NN` no conteúdo — material agrupado por tema.*")
        out.append("")

    # C) PDFs avulsos — cada um é uma aula
    out.append("## Aulas individuais (PDFs avulsos)\n")
    out.append(f"Total: {len(pdfs_aula)} PDFs no formato `COF - Aula NNN.pdf`. ")
    out.append("Aulas isoladas, sem data embutida no nome.\n")
    for s in pdfs_aula:
        m = re.search(r'Aula\s+(\d+)', s['title'])
        num = int(m.group(1))
        out.append(f"- **Aula {num:03d}** — `{s['title']}` — `source_id: {s['id']}`")
    out.append("")

    # D) Livros e ensaios do Olavo
    out.append("## Livros, ensaios e textos do Olavo\n")
    for s in livros_ensaios:
        out.append(f"- {s['title']} — `{s['type']}` — `{s['id']}`")
    out.append("")

    # E) Material complementar Unif_*
    out.append("## Material complementar (`Unif_*`)\n")
    for s in unif:
        clean = s['title'][len('Unif_'):]
        out.append(f"- {clean} — `{s['type']}` — `{s['id']}`")
    out.append("")

    # Resumo final
    total_aulas_compiladas = sum(
        len(parse_aulas_in_compilation(RAW / safe_filename(s['title'])))
        for s in compilations_year
        if (RAW / safe_filename(s['title'])).exists()
    )
    out.append("---\n")
    out.append("## Resumo\n")
    out.append(f"- Compilações por ano: **{len(compilations_year)}** "
               f"({total_aulas_compiladas} aulas numeradas detectadas)")
    out.append(f"- Compilações temáticas: **{len(compilations_theme)}**")
    out.append(f"- Aulas em PDF avulso: **{len(pdfs_aula)}**")
    out.append(f"- Livros/ensaios do Olavo: **{len(livros_ensaios)}**")
    out.append(f"- Material complementar Unif_*: **{len(unif)}**")
    out.append(f"- **Total de fontes no notebook:** {len(sources)}")
    out.append("")

    (ROOT / "01_fontes_e_aulas.md").write_text("\n".join(out), encoding='utf-8')
    print(f"Gerado 01_fontes_e_aulas.md ({len(''.join(out))} chars)")


if __name__ == "__main__":
    main()
