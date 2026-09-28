# Substitui fontes fracas (só resumo, captcha, recusadas) por arquivo ou URL alternativa.
# Adiciona a nova; só então apaga a antiga (mesma URL original) do notebook.
import json, subprocess, os, glob
NB = '4ac56794-d00a-436a-a446-24f1161cd9bd'; env = dict(os.environ, NLM_PROFILE='default')
def nlm(*a): return subprocess.run(['nlm', *a, '--profile', 'default'], capture_output=True, text=True, env=env, timeout=900)
S = {s['n']: s for s in json.load(open('selecionadas.json'))}
LT = 'https://human.libretexts.org/Bookshelves/Music/Music_Theory/Open_Music_Theory_2e_(Gotham_et_al.)/'
URL_NOVA = {8: LT + '04%3A_Diatonic_Harmony_Tonicization_and_Modulation/4.01%3A_Introduction_to_Harmony_Cadences_and_Phrase_Endings',
            9: LT + '07%3A_Popular_Music/7.09%3A_Four-Chord_Schemas', 10: LT + '07%3A_Popular_Music/7.13%3A_Pentatonic_Harmony'}
ARQ = {int(os.path.basename(f)[:3]): f for f in glob.glob('../05_arquivos_enviados/[0-9][0-9][0-9]*') if '_PMC' not in f}
lst = json.loads(nlm('source', 'list', NB, '--json').stdout)
lst = lst if isinstance(lst, list) else lst['sources']
for n in sorted(set(URL_NOVA) | set(ARQ)):
    s = S[n]; titulo = f"Ep{s['ep']:02d} · {s['titulo']}"[:200]
    antigas = [x['id'] for x in lst if (x.get('url') or '').rstrip('/') == s['url'].rstrip('/')]
    if n in URL_NOVA: r = nlm('source', 'add', NB, '--url', URL_NOVA[n], '--wait', '--json'); orig = URL_NOVA[n]
    else: r = nlm('source', 'add', NB, '--file', ARQ[n], '--title', titulo, '--wait', '--json'); orig = ARQ[n]
    try: sid = json.loads(r.stdout[r.stdout.find('{'):])['source_id']
    except Exception: print(n, 'FALHOU', (r.stdout + r.stderr)[-150:]); continue
    nlm('source', 'rename', sid, titulo, '--notebook', NB)
    w = len(nlm('source', 'content', sid).stdout.split())
    if antigas and w > 300: nlm('source', 'delete', *antigas, '--confirm')
    open('adicionadas_arquivo.jsonl', 'a').write(json.dumps(dict(n=n, ep=s['ep'], url=s['url'], substituto=orig, titulo=titulo, source_id=sid, palavras=w, apagadas=antigas), ensure_ascii=False) + '\n')
    print(n, w, 'palavras; apagou', len(antigas), '|', titulo[:60], flush=True)
