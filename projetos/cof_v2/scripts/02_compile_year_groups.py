#!/usr/bin/env python3
"""
Compila as transcrições convertidas em arquivos .md prontos para upload
em novo notebook NotebookLM.

Regras:
- Preferir versão Remasterizada quando existir (Aulas 1-40); senão Original.
- Agrupar por ano de apresentação (extraído do nome Aula_NNN-YYYY-MM-DD).
- Limite por arquivo: 450.000 palavras (margem de 10% sobre o teto NLM de 500k).
- NUNCA cortar uma aula no meio: se a próxima aula faria estourar o limite,
  fechar o arquivo atual e abrir YYYY-b, YYYY-c, etc.
- Cada aula entra com header `# Aula NNN — DD de mês de YYYY` para
  navegação fácil dentro do notebook.

Saída: ../compiladas/aulas/COF-Aulas-YYYY[-x].md
"""
import re, json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).parent.parent
MD_ORIG = ROOT / "_raw/dell_md/cof_original_transcricoes"
MD_REMAST = ROOT / "_raw/dell_md/cof_remasterizado_transcricoes"
OUT = ROOT / "compiladas/aulas"

WORD_LIMIT = 450_000
MONTHS_PT = ['janeiro','fevereiro','março','abril','maio','junho',
             'julho','agosto','setembro','outubro','novembro','dezembro']

AULA_RE = re.compile(r'^Aula_(\d{3,4})(?:-(\d{4}-\d{2}-\d{2}))?(?:_(\d+))?(?:-(.+))?$')

def fmt_date(iso: str) -> str:
    y, m, d = iso.split('-')
    return f"{int(d)} de {MONTHS_PT[int(m)-1]} de {y}"


def parse_aula(filename: str):
    """
    Aula_001-2009-03-14.md  → (1, '2009-03-14', None, None)
    Aula_006-2009-05-03_2.md → (6, '2009-05-03', '2', None)
    Aula_000-Apresentacao_do_COF.md → (0, None, None, 'Apresentacao_do_COF')
    """
    stem = Path(filename).stem
    m = AULA_RE.match(stem)
    if not m:
        return None
    num = int(m.group(1))
    date_iso = m.group(2)
    dup = m.group(3)
    rest = m.group(4)
    title_extra = None
    if not date_iso and rest is None:
        # caso Aula_NNN-Titulo (sem data) — re-parsear
        m2 = re.match(r'^Aula_(\d{3,4})-(.+)$', stem)
        if m2:
            title_extra = m2.group(2).replace('_',' ')
    elif not date_iso:
        title_extra = (rest or '').replace('_',' ')
    return num, date_iso, dup, title_extra


def collect_aulas():
    """
    Retorna lista ordenada de aulas (1 entrada por número), preferindo
    Remasterizado quando disponível.
    Cada entrada: {'num', 'date_iso', 'source', 'path', 'words', 'title_extra'}
    """
    seen = {}  # num → entry
    # Originais primeiro (depois sobrescrito por Remasterizadas)
    for path in sorted(MD_ORIG.glob('*.md')):
        info = parse_aula(path.name)
        if not info: continue
        num, date_iso, dup, title_extra = info
        text = path.read_text(encoding='utf-8', errors='replace')
        # Remover header inserido na conversão
        body = re.sub(r'^<!--.*?-->\n+', '', text, count=1, flags=re.DOTALL)
        # Para uma mesma Aula com múltiplos arquivos (dup, _2 etc), preferir
        # o sem dup; se ainda não houver entrada, registrar primeiro encontrado.
        prev = seen.get(num)
        if prev and not prev.get('dup_marker') and dup:
            continue
        seen[num] = {
            'num': num, 'date_iso': date_iso,
            'source': 'Original', 'path': str(path.relative_to(ROOT)),
            'words': len(body.split()), 'body': body,
            'title_extra': title_extra, 'dup_marker': dup,
        }
    # Remasterizados sobrescrevem
    for path in sorted(MD_REMAST.glob('*.md')):
        info = parse_aula(path.name)
        if not info: continue
        num, date_iso, dup, title_extra = info
        text = path.read_text(encoding='utf-8', errors='replace')
        body = re.sub(r'^<!--.*?-->\n+', '', text, count=1, flags=re.DOTALL)
        seen[num] = {
            'num': num, 'date_iso': date_iso,
            'source': 'Remasterizado', 'path': str(path.relative_to(ROOT)),
            'words': len(body.split()), 'body': body,
            'title_extra': title_extra, 'dup_marker': dup,
        }
    # Ordenar por (date, num); aulas sem data ficam por último
    return sorted(seen.values(),
                  key=lambda e: (e['date_iso'] or '9999-99-99', e['num']))


def group_by_year(aulas):
    groups = defaultdict(list)
    for a in aulas:
        y = (a['date_iso'] or '0000')[:4]
        if y == '0000': y = 'sem_data'
        groups[y].append(a)
    return groups


def split_to_files(year, aulas):
    """Quebra em -a, -b, ... respeitando WORD_LIMIT sem cortar aula."""
    files = [[]]
    cur_words = 0
    for a in aulas:
        if cur_words + a['words'] > WORD_LIMIT and files[-1]:
            files.append([])
            cur_words = 0
        files[-1].append(a)
        cur_words += a['words']
    return files


def render_compilation(year, idx, aulas, total_groups):
    suffix = ''
    if total_groups > 1:
        suffix = f"-{chr(ord('a')+idx)}"
    title = f"COF-Aulas-{year}{suffix}"
    parts = [
        f"# {title}\n",
        f"Compilação de aulas do Curso Online de Filosofia (Olavo de Carvalho).",
        f"**Período:** {year}  ",
        f"**Aulas incluídas:** {len(aulas)}  ",
        f"**Faixa:** Aula {aulas[0]['num']:03d}–{aulas[-1]['num']:03d}  ",
        f"**Palavras:** {sum(a['words'] for a in aulas):,}\n",
        "Cada aula é precedida por um cabeçalho `## Aula NNN — Data` para "
        "navegação. Conteúdo extraído das transcrições oficiais do COF (versão "
        "Remasterizada quando disponível, senão Original).\n",
        "---\n",
    ]
    for a in aulas:
        date_h = fmt_date(a['date_iso']) if a['date_iso'] else (a['title_extra'] or 's/data')
        parts.append(f"## Aula {a['num']:03d} — {date_h}")
        parts.append(f"*Fonte: {a['source']}*\n")
        parts.append(a['body'].strip())
        parts.append("\n---\n")
    return title, "\n".join(parts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    aulas = collect_aulas()
    print(f"Aulas únicas coletadas: {len(aulas)}")
    print(f"  Original:        {sum(1 for a in aulas if a['source']=='Original')}")
    print(f"  Remasterizado:   {sum(1 for a in aulas if a['source']=='Remasterizado')}")
    print(f"  Total palavras:  {sum(a['words'] for a in aulas):,}")

    groups = group_by_year(aulas)
    manifest = []
    for year in sorted(groups):
        ys = groups[year]
        files = split_to_files(year, ys)
        for idx, batch in enumerate(files):
            title, content = render_compilation(year, idx, batch, len(files))
            outpath = OUT / f"{title}.md"
            outpath.write_text(content, encoding='utf-8')
            manifest.append({
                'title': title, 'file': outpath.name,
                'year': year, 'aulas_count': len(batch),
                'aulas_range': [batch[0]['num'], batch[-1]['num']],
                'aulas': [a['num'] for a in batch],
                'words': sum(a['words'] for a in batch),
                'chars_estimated': sum(a['words'] for a in batch) * 6,
            })
            print(f"  ✓ {title}.md  aulas={len(batch):3d}  words={sum(a['words'] for a in batch):>7,}")

    (OUT.parent / "_aulas_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"\nTotal: {len(manifest)} arquivos compilados em {OUT}")


if __name__ == "__main__":
    main()
