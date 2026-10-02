"""Junta as três pesquisas numa lista bruta (_bruto.json), normaliza URL e marca o que já está no notebook (pesquisa 1)."""
import csv, io, json, re, pathlib
from collections import Counter
B = pathlib.Path(__file__).resolve().parent.parent
P1 = B.parent.parent / 'teoria_escuta_critica/deep_research/04_consolidacao/selecionadas.json'

def norm(u):
    u = (u or '').strip().rstrip('/.,;)').replace('http://', 'https://')
    u = re.sub(r'^https://www\.', 'https://', u)
    u = re.sub(r'[?#].*$', '', u) if 'youtube' not in u else u
    return u.lower()

def csv_block(path):
    txt = (B / path).read_text()
    blk = txt[txt.rindex('Parte F'):]
    m = re.search(r'```[a-z]*\n(.*?)```', blk, re.S)
    return list(csv.DictReader(io.StringIO(m.group(1)), delimiter=';'))

out = []
gpt = list(csv.DictReader(open(B / '01_chatgpt/fontes_glossario_musical_notebooklm.csv', encoding='utf-8-sig'), delimiter=';'))
for who, rows in [('chatgpt', gpt), ('claude', csv_block('02_claude_agent/resultado.md'))]:
    for r in rows:
        r = {k.strip().split(' ')[0]: (v or '').strip() for k, v in r.items() if k}
        out.append({'pesquisador': who, **r})
for rod in (1, 2):
    txt = (B / f'03_notebooklm_gemini/rodada{rod}_status_full.txt').read_text()
    blk = txt[txt.rindex('\n1. '):]  # lista de fontes no fim do relatório
    for m in re.finditer(r'^\s*(\d+)\.\s+(.*?)(?=^\s*\d+\.\s|\Z)', blk, re.M | re.S):
        raw = m.group(2); u = re.search(r'\((https?://[^)]+)\)', raw)
        t = ' '.join(raw.split()); u = re.sub(r'\s+', '', u.group(1)) if u else ''
        out.append({'pesquisador': 'notebooklm', 'id': f'N{rod}-{int(m.group(1)):02d}',
                    'titulo': re.sub(r',?\s*\(https?://.*$', '', t).rstrip(', '), 'url': u})
ja = {norm(s['url']): s['titulo'] for s in json.load(open(P1))}
for r in out:
    r['url_norm'] = norm(r.get('url', ''))
    r['ja_no_notebook'] = ja.get(r['url_norm'], '')
(B / '04_consolidacao/_bruto.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(Counter(r['pesquisador'] for r in out))
c = Counter(r['url_norm'] for r in out if r['url_norm'])
print('URLs únicas:', len(c), '| achadas por 2+:', sum(1 for u in c if len({r['pesquisador'] for r in out if r['url_norm'] == u}) > 1))
print('já no notebook:', [(r['pesquisador'], r['id']) for r in out if r['ja_no_notebook']])
print('sem URL:', [(r['pesquisador'], r['id']) for r in out if not r['url_norm']])
