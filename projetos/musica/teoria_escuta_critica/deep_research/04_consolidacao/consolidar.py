"""Decisão por fonte (3 pesquisadores) -> decisao_por_fonte.csv + selecionadas.json."""
import csv, json, re
from pathlib import Path
B = Path(__file__).resolve().parent
bruto = json.load(open(B/'_bruto.json'))
urls_gpt = {r['id']: r for r in csv.DictReader(open(B.parent/'01_chatgpt/urls_recuperadas.csv'), delimiter=';')}
http = {r['url']: r['code'] for r in csv.DictReader(open(B/'_http_check.tsv'), delimiter='\t')}

# ---- ChatGPT: decisão explícita (motivo) ou None = incluir com prioridade própria
DUP = 'duplicata de'
G = {
 'D1-01': ('dup', 'claude:D1-01'), 'D2-04': ('dup', 'claude:D2-02'), 'D3-01': ('dup', 'claude:D3-03'),
 'D4-03': ('dup', 'claude:D4-02'), 'D6-01': ('dup', 'claude:D6-01'), 'D6-02': ('dup', 'claude:D6-02'),
 'D7-01': ('dup', 'claude:D7-02'), 'D7-04': ('dup', 'claude:D7-10'), 'D7-05': ('dup', 'claude:D7-12'),
 'D7-06': ('dup', 'claude:D7-08'), 'D7-07': ('dup', 'claude:D7-09'), 'D7-08': ('dup', 'claude:D7-06'),
 'D8-01': ('dup', 'claude:D8-02'), 'D8-27': ('dup', 'claude:D8-29'),
 'D2-02': ('excluir', 'texto não conferido (bloqueio anti-robô); D2-01 e Claude D2 cobrem mixagem'),
 'D5-06': ('excluir', 'pago na Taylor & Francis, sem cópia aberta legítima (ChatGPT dizia "aberto"); vai para livros/artigos a adquirir'),
 'D8-09': ('excluir', 'autoria não confere e texto curto com playlist; Claude D8-07 cobre kołysanka'),
 'D8-10': ('excluir', 'catálogo de 100 fados, pouca prosa; UNESCO (Claude D8-08) cobre'),
 'D8-11': ('excluir', 'encarte escaneado sem texto (precisaria OCR); Claude D8-10/D8-11 cobrem flamenco'),
 'D8-13': ('excluir', 'plano de aula de dança argentina, não de escuta; Claude D8-13/D8-14 cobrem tango'),
 'D8-14': ('excluir', 'não existe página de klezmer no Folkways (só gênero Judaica, não conferido); Claude D8-15 cobre'),
 'D8-15': ('excluir', 'dissertação sobre rebetiko na diáspora de Nova York, fora do foco; Claude D8-16/D8-17 cobrem'),
 'D8-17': ('excluir', 'encarte escaneado sem texto; Claude D8-19 (Rāgs Around the Clock) cobre raga'),
 'D8-22': ('excluir', 'encarte escaneado sem texto; Claude D8-23 cobre kora'),
 'D8-23': ('excluir', 'só existe como slides .pptx no Zenodo, não texto corrido; Claude D8-24/D8-25 cobrem'),
 'D8-28': ('excluir', 'encarte com OCR ruim; Claude D8-30 cobre a nuba andaluza'),
 'D8-03': ('excluir', 'dissertação sobre Stravinsky; Claude D8-04/D8-05 cobrem znamenny'),
}
PRIO_G = {'D5-04': '3', 'D3-02': '3', 'D3-03': '3', 'D8-05': '3', 'D8-07': '3', 'D8-19': '3', 'D8-21': '3',
          'D8-16': '3', 'D9-03': '3', 'D8-08': '2', 'D8-12': '2', 'D8-26': '2', 'D8-25': '2', 'D8-29': '2',
          'D9-01': '2', 'D9-02': '2', 'D5-07': '2', 'D5-01': '2', 'D8-18': '1', 'D5-05': '1'}
NOTA_G = {'D8-19': 'texto em japonês — única fonte verificada sobre enka',
          'D8-21': 'encarte curto (2 págs.) — única fonte sobre koto',
          'D8-04': 'texto em russo', 'D8-05': 'texto em russo',
          'D8-06': 'encarte de 6 págs.; única fonte sobre romance cigano russo',
          'D1-02': 'ChatGPT errou o periódico: é Annals of the NY Academy of Sciences (2018)',
          'D5-02': 'manuscrito do autor (2005); o capítulo publicado é fechado',
          'D4-05': 'texto integral do Everyday Tonality II publicado pelo próprio autor (HTML, ~117 mil palavras, sem exemplos musicais nem figuras) — conferido 28/09',
          'D2-03': 'é artigo da revista TISMIR, não dos anais'}

# ---- NotebookLM: incluir só estas; o resto é excluído com motivo por categoria
N_INC = {'N1-11': '2', 'N1-18': '1', 'N1-19': '3', 'N1-25': '2', 'N1-30': '3', 'N2-03': '2'}
N_DUP = {'N1-01': 'claude:D1-01', 'N1-05': 'claude:D6-03', 'N1-10': 'claude:D2-02', 'N1-15': 'claude:D2-02'}
def motivo_n(r):
    u = r['url'].lower(); c = http.get(r['url'], '')
    for k, m in [('scribd', 'cópia no Scribd (excluído por regra)'), ('dokumen.pub', 'cópia não autorizada (dokumen.pub)'),
                 ('researchgate', 'ResearchGate bloqueia leitura (403)'), ('facebook', 'post de Facebook'),
                 ('wikipedia', 'Wikipedia: não assinada; fontes primárias já cobrem'), ('academia.edu', 'Academia.edu bloqueia leitura'),
                 ('alamy', 'banco de imagens'), ('melodigging', 'agregador sem autoria'),
                 ('blogspot', 'blog'), ('psychologytoday', 'blog de divulgação'), ('decisionlab', 'divulgação de marketing'),
                 ('advergize', 'marketing'), ('jukee', 'marketing'), ('siriusxm', 'marketing'), ('xaluca', 'agência de turismo'),
                 ('astrolabe', 'agência de turismo'), ('restaurantchezali', 'site de restaurante'), ('radarmusica', 'blog'),
                 ('archive.org/stream', 'livro comercial em cópia não autorizada'), ('mdpi', 'bloqueia leitura (403) e fora do foco'),
                 ('oup.com', 'bloqueia leitura (403)'), ('scholarcommons', 'bloqueia leitura (403)'),
                 ('ich.unesco.org/doc', 'PDF não abre (devolve HTML); UNESCO já coberta por páginas dos elementos')]:
        if k in u: return m
    return 'fora do foco da ficha ou técnico demais para leigo; tema já coberto por fonte melhor'

linhas, sel = [], []
def add_sel(pesq, id_, r, url, prio, nota=''):
    sel.append({'n': len(sel)+1, 'origem': f'{pesq}:{id_}', 'dominio': (r.get('dominio') or '')[:2],
                'item_da_ficha': r.get('item_da_ficha', ''), 'prioridade': prio, 'titulo': r['titulo'],
                'autor': r.get('autor_instituicao', ''), 'url': url, 'episodio': r.get('episodio_sugerido', ''),
                'nivel': r.get('nivel', ''), 'nota': nota})
    return len(sel)

for r in bruto:
    p, i = r['pesquisador'], r['id']
    if p == 'claude':
        n = add_sel(p, i, r, r['url'], r.get('prioridade', '2'),
                    'abre só por http; pode precisar subir como arquivo' if r['url'].startswith('http://') else '')
        linhas.append((p, i, r['titulo'], r['url'], 'incluir', f'selecionada #{n}'))
    elif p == 'chatgpt':
        u = urls_gpt.get(i, {}); url = u.get('url', '')
        d = G.get(i)
        if d and d[0] == 'dup': linhas.append((p, i, r['titulo'], url, 'excluir', f'{DUP} {d[1]}'))
        elif d: linhas.append((p, i, r['titulo'], url, 'excluir', d[1]))
        else:
            n = add_sel(p, i, r, url, PRIO_G.get(i, re.sub(r'\D', '', r.get('prioridade', '')) or '2'), NOTA_G.get(i, ''))
            linhas.append((p, i, r['titulo'], url, 'incluir', f'selecionada #{n}'))
    else:
        if i in N_DUP: linhas.append((p, i, r['titulo'], r['url'], 'excluir', f'{DUP} {N_DUP[i]}'))
        elif i in N_INC:
            n = add_sel(p, i, {**r, 'dominio': 'D8' if i.startswith('N2') else ''}, r['url'], N_INC[i])
            linhas.append((p, i, r['titulo'], r['url'], 'incluir', f'selecionada #{n}'))
        else: linhas.append((p, i, r['titulo'], r['url'], 'excluir', motivo_n(r)))

# ---- correções manuais (linha deslocada no CSV do ChatGPT; domínio/episódio do NotebookLM)
FIX = {'chatgpt:D1-03': dict(titulo='Repeated Listening Increases the Liking for Music Regardless of Its Complexity',
                             autor='Guy Madison; Gunilla Schiölde (Frontiers in Neuroscience)', episodio='1 método', prioridade='2'),
       'notebooklm:N1-11': dict(dominio='D2', episodio='2 produção/mixagem', autor='arXiv (revisão)'),
       'notebooklm:N1-18': dict(dominio='D6', episodio='6 forma', autor='Ralf von Appen; Markus Frei-Hauenschild (Samples, GfPM, 2015)'),
       'notebooklm:N1-19': dict(dominio='D6', episodio='6 forma', autor='Stroud / Music Theory Online'),
       'notebooklm:N1-25': dict(dominio='D5', episodio='5 letra', autor='ACL Anthology (NLP4DH 2025)'),
       'notebooklm:N1-30': dict(dominio='D5', episodio='5 letra', autor='Chartered Institute of Linguists'),
       'notebooklm:N2-03': dict(episodio='8+ tradições do mundo', autor='Seifed-Din Shehadeh Abdoun (tese, U. Maryland)')}
for x in sel:
    x.update(FIX.get(x['origem'], {}))
    if x['origem'] == 'chatgpt:D1-03':
        linhas[:] = [(a, b, x['titulo'] if (a, b) == ('chatgpt', 'D1-03') else c, d, e, f) for a, b, c, d, e, f in linhas]

with open(B/'decisao_por_fonte.csv', 'w', newline='') as f:
    w = csv.writer(f, delimiter=';'); w.writerow(['pesquisador', 'id', 'titulo', 'url', 'decisao', 'motivo']); w.writerows(linhas)
json.dump(sel, open(B/'selecionadas.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print('linhas:', len(linhas), Counter(l[4] for l in linhas))
print('selecionadas:', len(sel), 'por prioridade', sorted(Counter(s['prioridade'] for s in sel).items()))
print('por origem', Counter(s['origem'].split(':')[0] for s in sel))
print('sem url:', [s['origem'] for s in sel if not s['url'].startswith('http')])
