# Insere as fontes selecionadas no notebook da perícia (tarefa notebooklm_edson-ll06).
# Idempotente: pula URLs já registradas em adicionadas.jsonl.
import json, subprocess, os
NB='1af19855-4523-4ba9-8837-343f474a2a83'
ENV=dict(os.environ, NLM_PROFILE='default')
DOM={'D1':'Previdência/BPC','D2':'Perícia judicial','D3':'Ética/CFM','D4':'Trabalho/nexo','D5':'Baremos','D6':'Classificações','D7':'Evidência','D8':'Criminal'}
def nlm(*a, timeout=900):
    return subprocess.run(['nlm',*a,'--profile','default'],capture_output=True,text=True,env=ENV,timeout=timeout)
feitos={json.loads(l)['url'] for l in open('adicionadas.jsonl')} if os.path.exists('adicionadas.jsonl') else set()
for i,s in enumerate(json.load(open('selecionadas.json')),1):
    if s['url'] in feitos: continue
    titulo=f"Atual 2026 · {DOM[s['dominio']]} · {s['titulo']}"
    reg=dict(n=i,url=s['url'],titulo=titulo)
    if s['url']=='https://sistemas.cfm.org.br/normas/arquivos/resolucoes/BR/2025/2430_2025.pdf':
        reg['source_id']='1fd2d061-08b5-4720-b970-de1b98609bbc'
    else:
        r=nlm('source','add',NB,'--url',s['url'],'--wait','--json')
        try: reg['source_id']=json.loads(r.stdout[r.stdout.find('{'):])['source_id']
        except Exception: reg['erro']=(r.stdout+r.stderr)[-400:]
    if 'source_id' in reg:
        nlm('source','rename',reg['source_id'],titulo)
        c=nlm('source','content',reg['source_id'],timeout=120)
        reg['palavras']=len(c.stdout.split())
    open('adicionadas.jsonl','a').write(json.dumps(reg,ensure_ascii=False)+'\n')
    print(i, reg.get('palavras', reg.get('erro','')[:80]), titulo[:80], flush=True)
