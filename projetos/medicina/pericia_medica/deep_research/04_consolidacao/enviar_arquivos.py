# Sobe como arquivo as fontes cujo site bloqueia o leitor do NotebookLM (2ª passada, notebooklm_edson-ll06).
import json,subprocess,os,sys
NB='1af19855-4523-4ba9-8837-343f474a2a83'
DOM={'D1':'Previdência/BPC','D2':'Perícia judicial','D3':'Ética/CFM','D4':'Trabalho/nexo','D5':'Baremos','D6':'Classificações','D7':'Evidência','D8':'Criminal'}
sel=json.load(open('04_consolidacao/selecionadas.json'))
REG='04_consolidacao/adicionadas_arquivo.jsonl'
feitos={json.loads(l)['n'] for l in open(REG)} if os.path.exists(REG) else set()
def nlm(*a,t=900): return subprocess.run(['nlm',*a,'--profile','default'],capture_output=True,text=True,timeout=t)
for n in map(int,sys.argv[1:]):
    if n in feitos: continue
    s=sel[n-1]; titulo=f"Atual 2026 · {DOM[s['dominio']]} · {s['titulo']}"
    r=nlm('source','add',NB,'--file',f'05_arquivos_enviados/{n:02d}.md','--wait','--json')
    reg=dict(n=n,url=s['url'],titulo=titulo,arquivo=f'05_arquivos_enviados/{n:02d}.md')
    try: reg['source_id']=json.loads(r.stdout[r.stdout.find('{'):])['source_id']
    except Exception: reg['erro']=(r.stdout+r.stderr)[-300:]
    if 'source_id' in reg:
        nlm('source','rename',reg['source_id'],titulo)
        c=nlm('source','content',reg['source_id'],t=180); reg['palavras']=len(c.stdout.split())
    open(REG,'a').write(json.dumps(reg,ensure_ascii=False)+'\n')
    print(n,reg.get('palavras',reg.get('erro','')[:80]),titulo[:70],flush=True)
