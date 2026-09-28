# Insere as 135 fontes aprovadas (Edson, 2026-09-28) no notebook "Teoria musical para escuta crítica".
# Tarefa notebooklm_edson-c0x3. Idempotente: pula URLs já registradas em adicionadas.jsonl.
# Título no notebook: "EpNN · <título>" — cada episódio seleciona suas fontes por esse prefixo.
import json, subprocess, os
NB = '4ac56794-d00a-436a-a446-24f1161cd9bd'
ENV = dict(os.environ, NLM_PROFILE='default')
def nlm(*a, timeout=900):
    return subprocess.run(['nlm', *a, '--profile', 'default'], capture_output=True, text=True, env=ENV, timeout=timeout)
feitos = {json.loads(l)['url'] for l in open('adicionadas.jsonl')} if os.path.exists('adicionadas.jsonl') else set()
for s in json.load(open('selecionadas.json')):
    if s['url'] in feitos: continue
    titulo = f"Ep{s['ep']:02d} · {s['titulo']}"[:200]
    reg = dict(n=s['n'], ep=s['ep'], url=s['url'], titulo=titulo)
    try:
        r = nlm('source', 'add', NB, '--url', s['url'], '--wait', '--json')
        reg['source_id'] = json.loads(r.stdout[r.stdout.find('{'):])['source_id']
    except Exception as e:
        reg['erro'] = (getattr(r, 'stdout', '') + getattr(r, 'stderr', '') if 'r' in dir() else str(e))[-400:]
    if 'source_id' in reg:
        nlm('source', 'rename', reg['source_id'], titulo, '--notebook', NB)
        c = nlm('source', 'content', reg['source_id'], timeout=120)
        reg['palavras'] = len(c.stdout.split())
    open('adicionadas.jsonl', 'a').write(json.dumps(reg, ensure_ascii=False) + '\n')
    print(s['n'], reg.get('palavras', reg.get('erro', '')[:80]), titulo[:80], flush=True)
