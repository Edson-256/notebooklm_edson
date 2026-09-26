# Baixa as fontes que o NotebookLM não conseguiu ler pela URL e gera .md limpos para upload.
# Planalto: remove texto tachado (<strike>/<s>/<del>) = redação revogada no texto compilado.
import json,re,html,subprocess,sys,os
OUT='05_arquivos_enviados'
UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 Safari/605.1.15'
def get(u):
    return subprocess.run(['curl','-sL','-m','120','-A',UA,u],capture_output=True).stdout
def dec(b):
    m=re.search(rb'charset=["\']?([\w-]+)',b[:3000]); enc=(m.group(1).decode() if m else 'utf-8')
    try: return b.decode(enc)
    except: return b.decode('latin-1')
def html2txt(t):
    t=re.sub(r'(?is)<(script|style|head|nav|footer)\b.*?</\1>','',t)
    t=re.sub(r'(?is)<(strike|s|del)\b[^>]*>.*?</\1>','',t)
    t=re.sub(r'(?i)<br\s*/?>|</p>|</div>|</tr>|</h\d>|</li>','\n',t)
    t=html.unescape(re.sub(r'<[^>]+>',' ',t))
    t='\n'.join(' '.join(l.split()) for l in t.splitlines()); t=re.sub(r'\n{3,}','\n\n',t)
    return t.strip()
def dou(t):
    x=html2txt(t); i=x.find('Órgão:'); j=x.find('Este conteúdo não substitui')
    return x[i:j if j>0 else None] if i>=0 else x
def pmc_xml(pmcid):
    x=get(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML').decode('utf-8','ignore')
    if '<article' not in x: return ''
    x=re.sub(r'(?s)<ref-list.*?</ref-list>','',x)
    x=re.sub(r'</(title|p|sec|caption|td|th|tr)>','\n',x)
    return html2txt(x)
sel=json.load(open('04_consolidacao/selecionadas.json'))
add={json.loads(l)['n']:json.loads(l) for l in open('04_consolidacao/adicionadas.jsonl')}
alvos=[int(a) for a in sys.argv[1:]]
for n in alvos:
    s=sel[n-1]; u=s.get('url')
    m=re.search(r'PMC\d+',u)
    if m: txt=pmc_xml(m.group(0))
    elif u.lower().endswith('.pdf'):
        open('/tmp/_x.pdf','wb').write(get(u)); txt=subprocess.run(['pdftotext','-layout','/tmp/_x.pdf','-'],capture_output=True,text=True).stdout
    elif 'in.gov.br' in u: txt=dou(dec(get(u)))
    else: txt=html2txt(dec(get(u)))
    f=f'{OUT}/{n:02d}.md'
    open(f,'w').write(f"# {s['titulo']}\n\nFonte oficial: {u}\nBaixado em 2026-09-26 (texto tachado/revogado removido quando presente).\n\n{txt}\n")
    print(n, len(txt.split()), s['titulo'][:70])
