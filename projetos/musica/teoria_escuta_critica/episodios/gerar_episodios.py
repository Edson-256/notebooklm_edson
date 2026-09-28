# Gera os episódios de áudio do notebook "Teoria musical para escuta crítica" (tarefa notebooklm_edson-c0x3).
# Uso: gerar_episodios.py --criar 1 2 3   |   --status   |   --baixar
# Fontes de cada episódio = títulos que começam com "EpNN ·" (+ EXTRA). Estado em estado.json.
import json, re, subprocess, os, sys, time
NB = '4ac56794-d00a-436a-a446-24f1161cd9bd'
ENV = dict(os.environ, NLM_PROFILE='default')
AQUI = os.path.dirname(os.path.abspath(__file__)); ESTADO = os.path.join(AQUI, 'estado.json')
TITULOS = {1: 'Como ouvir com método', 2: 'Produção e mixagem', 3: 'Melodia', 4: 'Harmonia sem jargão',
           5: 'Letra - prosódia, rima, métrica e transcriação', 6: 'Forma', 7: 'Contexto e função social',
           8: 'Tradições do mundo 1 - Mediterrâneo, árabe e ibérico', 9: 'Tradições do mundo 2 - Leste europeu',
           10: 'Tradições do mundo 3 - Ásia e África'}
EXTRA = {9: ['Beyond the Classroom'], 10: ['Beyond the Classroom']}  # fonte geral de world music
def nlm(*a, timeout=300):
    return subprocess.run(['nlm', *a, '--profile', 'default'], capture_output=True, text=True, env=ENV, timeout=timeout)
def prompts():
    t = open(os.path.join(AQUI, 'prompts_episodios.md')).read()
    blocos = dict(re.findall(r'^## (COMMON|Ep\d\d)[^\n]*\n+```text\n(.*?)```', t, re.S | re.M))
    return {int(k[2:]): blocos['COMMON'].strip() + '\n\n' + v.strip() for k, v in blocos.items() if k != 'COMMON'}
def fontes(ep):
    L = json.loads(nlm('source', 'list', NB, '--json').stdout); L = L if isinstance(L, list) else L['sources']
    return [s['id'] for s in L if s['status'] == 2 and (s['title'].startswith(f'Ep{ep:02d} ·')
            or any(x in s['title'] for x in EXTRA.get(ep, [])))]
def carregar(): return json.load(open(ESTADO)) if os.path.exists(ESTADO) else {}
def salvar(e): json.dump(e, open(ESTADO, 'w'), ensure_ascii=False, indent=1)
if sys.argv[1] == '--checar':
    for ep, p in prompts().items(): print(ep, len(p), 'chars', len(fontes(ep)), 'fontes')
elif sys.argv[1] == '--criar':
    est = carregar(); P = prompts()
    for ep in map(int, sys.argv[2:]):
        ids = fontes(ep)
        r = nlm('audio', 'create', NB, '--format', 'deep_dive', '--length', 'default', '--language', 'pt-BR',
                '--focus', P[ep], '--source-ids', ','.join(ids), '--confirm', '--json')
        out = r.stdout + r.stderr
        m = re.search(r'"(?:artifact_id|id)"\s*:\s*"([^"]+)"', out)
        est[str(ep)] = dict(titulo=TITULOS[ep], fontes=len(ids), artifact_id=m.group(1) if m else None,
                            criado=time.strftime('%Y-%m-%d %H:%M'), saida=out[-300:] if not m else '')
        salvar(est); print(ep, 'ok' if m else 'FALHOU', m.group(1) if m else out[-200:], flush=True)
elif sys.argv[1] == '--status':
    print(nlm('studio', 'status', NB, '--json', timeout=120).stdout[:4000])
elif sys.argv[1] == '--baixar':
    est = carregar(); os.makedirs(os.path.join(AQUI, 'audios'), exist_ok=True)
    for ep, e in sorted(est.items(), key=lambda x: int(x[0])):
        if not e.get('artifact_id') or e.get('arquivo'): continue
        arq = os.path.join(AQUI, 'audios', f"{int(ep):02d} - {e['titulo']}.m4a")
        r = nlm('download', 'audio', NB, '--id', e['artifact_id'], '--output', arq, timeout=600)
        if os.path.exists(arq) and os.path.getsize(arq) > 500_000: e['arquivo'] = arq; salvar(est); print(ep, 'baixado', arq)
        else: print(ep, 'ainda não', (r.stdout + r.stderr)[-150:])
