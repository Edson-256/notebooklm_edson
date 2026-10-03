# Insere as 101 fontes aprovadas (Edson, 2026-10-01) no notebook "Teoria musical para escuta crítica".
# Tarefa notebooklm_edson-mmf9. Idempotente: pula o que já está em adicionadas.jsonl com source_id.
# Título no notebook: "Gloss · <família> · <título>" — separa estas fontes das "EpNN ·" da pesquisa 1.
# Campo `arquivo` em selecionadas.json => sobe ../05_arquivos_enviados/<arquivo>; senão, por URL.
import json, subprocess, os
NB = '4ac56794-d00a-436a-a446-24f1161cd9bd'
ENV = dict(os.environ, NLM_PROFILE='default')
def nlm(*a, timeout=900):
    return subprocess.run(['nlm', *a, '--profile', 'default'], capture_output=True, text=True, env=ENV, timeout=timeout)
feitos = set()
if os.path.exists('adicionadas.jsonl'):
    feitos = {json.loads(l)['n'] for l in open('adicionadas.jsonl') if json.loads(l).get('source_id')}
for s in json.load(open('selecionadas.json')):
    if s['n'] in feitos or s.get('pendente'): continue
    titulo = f"Gloss · {s['familia']} · {s['titulo']}"[:200]
    reg = dict(n=s['n'], familia=s['familia'], url=s['url'], arquivo=s.get('arquivo', ''), titulo=titulo)
    r = None
    try:
        if s.get('arquivo'):
            r = nlm('source', 'add', NB, '--file', f"../05_arquivos_enviados/{s['arquivo']}", '--wait', '--json')
        else:
            r = nlm('source', 'add', NB, '--url', s['url'], '--wait', '--json')
        reg['source_id'] = json.loads(r.stdout[r.stdout.find('{'):])['source_id']
    except Exception as e:
        reg['erro'] = ((r.stdout + r.stderr) if r else str(e))[-400:]
    if reg.get('source_id'):
        nlm('source', 'rename', reg['source_id'], titulo, '--notebook', NB)
        c = nlm('source', 'content', reg['source_id'], timeout=180)
        reg['palavras'] = len(c.stdout.split())
    open('adicionadas.jsonl', 'a').write(json.dumps(reg, ensure_ascii=False) + '\n')
    print(s['n'], reg.get('palavras', reg.get('erro', '')[:100]), titulo[:80], flush=True)
