"""Junta as três pesquisas numa lista bruta (_bruto.json) e agrupa por URL normalizada."""
import csv, io, json, re, pathlib
B = pathlib.Path(__file__).resolve().parent.parent

def csv_block(path):
    txt = (B / path).read_text()
    i = txt.index('Parte F'); blk = txt[i:]
    m = re.search(r'```[a-z]*\n(.*?)```', blk, re.S)
    rows = list(csv.DictReader(io.StringIO(m.group(1)), delimiter=';'))
    return rows

def norm(u):
    u = u.strip().rstrip('/.,;)').replace('http://', 'https://')
    u = re.sub(r'^https://www\.', 'https://', u)
    u = re.sub(r'[?#].*$', '', u) if 'youtube' not in u else u
    return u.lower()

out = []
for who, path in [('chatgpt', '01_chatgpt/resultado.md'), ('claude', '02_claude_agent/resultado.md')]:
    for r in csv_block(path):
        r = {k.strip().split(' ')[0]: (v or '').strip() for k, v in r.items() if k}
        out.append({'pesquisador': who, **r})
for rod in (1, 2):
    txt = (B / f'03_notebooklm_gemini/rodada{rod}_status_full.txt').read_text()
    for m in re.finditer(r'^\s*(\d+)\.\s+(.*?),\s*\((https?://[^)\s]+)\)\s*$', txt, re.M):
        out.append({'pesquisador': 'notebooklm', 'id': f'N{rod}-{int(m.group(1)):02d}',
                    'titulo': m.group(2).strip(), 'url': m.group(3), 'dominio': 'D8' if rod == 2 else ''})
for r in out:
    r['url_norm'] = norm(r.get('url', ''))
(B / '04_consolidacao/_bruto.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
from collections import Counter
print(Counter(r['pesquisador'] for r in out))
print('URLs únicas:', len({r['url_norm'] for r in out}))
c = Counter(r['url_norm'] for r in out)
print('achadas por 2+ pesquisadores:', sum(1 for u in c if len({r['pesquisador'] for r in out if r['url_norm']==u})>1))
print('colunas chatgpt:', list(next(r for r in out if r['pesquisador']=='chatgpt').keys()))
