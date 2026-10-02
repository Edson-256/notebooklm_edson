"""Decisão por fonte (3 pesquisadores) -> decisao_por_fonte.csv + selecionadas.json.

Regra: o agente Claude entra por padrão (abriu cada URL e trouxe a notação/os trechos);
o ChatGPT entra quando acrescenta fonte própria; o NotebookLM só quando passa nos critérios.
Conferências feitas nesta sessão (2026-10-01) estão nos motivos.
"""
import csv, json, re
from pathlib import Path
B = Path(__file__).resolve().parent
bruto = json.load(open(B / '_bruto.json'))
DUP = 'duplicata de'

# ---- substituições de URL (página de repositório -> PDF; arquivo baixado e subido à mão)
URL = {
    'chatgpt:F2-02': 'https://anaforas.fic.edu.uy/jspui/bitstream/123456789/101481/1/Ayesta_Milonga_SELDIA784.pdf',
    'chatgpt:F1-04': 'https://revistas.usp.br/revistadatulha/article/download/121319/129293',
    'chatgpt:F5-02': 'https://teses.usp.br/teses/disponiveis/27/27157/tde-07032013-145429/publico/EnriqueMestrado.pdf',
    'claude:F3-03': 'https://yorkspace.library.yorku.ca/bitstreams/bfa1f800-2480-443c-b1c5-1d38832d2186/download',
}
ARQ = {  # subir como arquivo (05_arquivos_enviados/): o servidor não entrega o PDF a leitor automático
    'claude:F1-01': 'correa_viola_caipira_usp.pdf',
    'claude:F1-02': 'vilela_cantando_propria_historia_usp.pdf',
    'claude:F2-06': 'wolffenbuttel_musica_rs.pdf',
    'claude:F3-02': 'castela_guitarra_coimbra.pdf',
}

# ---- ChatGPT: decisão explícita; ausente = incluir com a prioridade dele
G = {
    'F1-01': ('dup', 'claude:F1-07 (página-índice do mesmo dossiê; o PDF está em claude:F1-07)'),
    'F1-02': ('excluir', 'foco em difusão audiovisual do fandango, não descrição musical; dossiê (claude:F1-07) cobre'),
    'F1-03': ('dup', 'claude:F1-06 (mesmo artigo de Garcia, versão SciELO)'),
    'F1-05': ('excluir', 'página-resumo do IPHAN; o dossiê completo (claude:F1-07) cobre'),
    'F1-06': ('excluir', 'parecer administrativo; o dossiê completo (claude:F1-07) cobre'),
    'F2-01': ('dup', 'claude:F2-01'),
    'F2-03': ('excluir', 'URL errada: o handle aponta para uma dissertação de filosofia política, não para "Campeirismo musical" — conferido no PDF em 01/10'),
    'F2-04': ('excluir', 'site amador, 404; o Manual de danças gaúchas vai para a lista de livros a adquirir'),
    'F2-05': ('excluir', 'texto da decisão do Comitê; a página do elemento (claude:F2-01) cobre'),
    'F3-01': ('excluir', 'plano curricular de 3 páginas (só a lista de fados-base); Sergl (claude:F3-01) descreve os mesmos fados'),
    'F3-02': ('excluir', 'inacessível (403 no curl e no WebFetch); Castela (claude:F3-02) cobre a canção de Coimbra'),
    'F3-04': ('excluir', 'página inicial do Museu do Fado, sem texto substantivo'),
    'F5-03': ('dup', 'claude:F5-04 (mesmo artigo de Souza na Opus)'),
    'F5-04': ('excluir', 'história política da bossa nova, sem descrição musical'),
    'F5-05': ('excluir', 'notícia do Jornal da Unicamp, 404'),
    'F5-06': ('excluir', 'jazz e Laurindo Almeida: lateral ao reconhecimento da bossa nova'),
    'F6-01': ('dup', 'claude:F6-01 (o mesmo dossiê técnico; o link do gov.br devolve HTML)'),
    'F6-02': ('dup', 'claude:F6-01 (página-índice do mesmo processo)'),
    'F6-03': ('excluir', 'anais da Compós, 404'),
    'F6-04': ('excluir', 'foco em autoria feminina, não em descrição musical de modinha/seresta'),
    'F7-01': ('dup', 'claude:F7-03'),
    'F7-02': ('excluir', 'é só a ficha bibliográfica do Handbook of Latin American Studies (403), não o texto de Torres'),
    'F7-03': ('excluir', 'inacessível (403 no curl e no WebFetch) — tentar no navegador: é das poucas pistas de bolero mexicano'),
    'F8-01': ('dup', 'claude:F8-01'),
    'F8-02': ('excluir', 'site pessoal, sem resposta (timeout)'),
    'F8-03': ('excluir', 'catálogo de acervo sonoro, sem texto analítico'),
    'F8-04': ('excluir', 'notícia catalográfica de um disco, sem texto analítico'),
    'F8-05': ('excluir', 'registro de catálogo da BnF, sem texto'),
    'F9-01': ('excluir', 'página-resumo do IPHAN; o dossiê completo (claude:F9-01) cobre'),
    'F9-02': ('excluir', 'página-resumo do IPHAN; o dossiê completo (claude:F9-01) cobre'),
    'F9-03': ('excluir', 'parecer do conselho; o dossiê completo (claude:F9-01) cobre'),
    'F9-04': ('excluir', 'notícia do IPHAN, 404'),
    'F9-05': ('excluir', 'notícia do IPHAN, 401'),
    'F10-01': ('excluir', 'encarte escaneado sem camada de texto (0 palavras extraídas; precisaria OCR)'),
    'F10-02': ('excluir', 'plano de aula inexistente nessa URL (404)'),
    'F10-04': ('excluir', 'página do Festival 1988 sem resposta (timeout); não conferida'),
    'F10-05': ('excluir', 'inacessível (403); canto da corte de São Petersburgo é lateral — znamenny coberto por claude:F10-01/F10-02'),
    'F10-06': ('excluir', 'já está no notebook (fonte "Ep09 · Znamenny Chant for the 21st Century")'),
    'T-01': ('dup', 'claude:T-01'),
    'T-02': ('excluir', 'URL errada (404); o capítulo certo está em claude:T-02'),
    'T-03': ('dup', 'claude:T-05'),
    'T-05': ('dup', 'claude:T-04'),
    'T-06': ('dup', 'claude:T-08'),
    'T-07': ('excluir', 'URL errada (404); escalas maiores ficam com Schmidt-Jones e as apostilas em pt (claude:T-17/T-18)'),
    'T-09': ('dup', 'claude:T-06'),
    'T-11': ('dup', 'claude:T-09'),
}
PRIO_G = {'F1-04': '2', 'F2-02': '2', 'F4-01': '3', 'F4-07': '3', 'F10-03': '3'}
NOTA_G = {
    'F2-02': 'Ayestarán: 2 págs. digitalizadas com OCR imperfeito (~2.800 palavras) — única fonte uruguaia clássica sobre a milonga',
    'F4-01': 'material de curso de gestão cultural; usar só os capítulos de música',
    'F4-07': 'lista de gravações por palo — serve de guia de escuta',
    'F10-03': 'encarte curto de conjunto de balalaica em formato orquestral — "tradição inventada" segundo Morgenstern (claude:F10-06)',
    'F5-02': 'servidor da USP não respondeu daqui; existência e PDF conferidos pela página da tese (WebFetch, 01/10)',
}

# ---- Claude: incluir; exceções
C = {
    'F6-08': ('pendente', 'bloqueado por Cloudflare (403) — conferir no navegador; é a única fonte sobre samba de breque'),
    'T-21': ('excluir', 'lição interativa em JavaScript, sem texto legível para o NotebookLM'),
    'T-19': ('excluir', 'página-índice das unidades do curso (~600 palavras), sem o conteúdo das aulas'),
}
PRIO_C = {'F4-02': '3', 'F7-03': '3'}
NOTA_C = {
    'F3-01': 'ORIGEM CONTESTADA: Sergl afirma que o fado foi "gênero inicialmente popular no Brasil" e migrou "provavelmente em 1821" — conferido no texto; não usar sem Nery. Afinações Lisboa × Coimbra conferidas (p. 12, citando Henrique 1994)',
    'F6-01': 'forma AABBACCA (três partes de 16 compassos) e variante binária AA|BB|A — conferido no dossiê',
    'F1-04': 'guarânia: semínima pontuada ≈ 70 em 6/8; versões brasileiras oscilam para 3/4 — conferido',
    'F2-02': 'chamamé: "birritmia del 6/8 y 3/4" — conferido',
    'F2-06': 'vaneira em 2/4 de origem habanera, três células: (a) colcheia pontuada/semicolcheia/colcheia/colcheia; (b) idem com a semicolcheia ligada; (c) colcheia/2 semicolcheias/colcheia/colcheia; vaneirão = mesma base, mais rápido. Chamamé em 3/4 com acento no 3º tempo (puxada de fole), o que o diferencia da rancheira — conferido 02/10',
    'F9-02': 'baião: trechos em dórico e em mixolídio, em exemplos notados — conferido',
    'F4-05': 'artigo acadêmico hospedado num blog de violão (laguitarra-blog); a fonte é o artigo, não o blog',
    'F1-03': 'PDF grande (13,9 MB)',
    'F8-05': 'site autoral sem vínculo institucional; usar só com corroboração de F8-03/F8-04',
    'F7-06': 'radiorreportagem (UNAM) — fraca, mas única fonte aberta sobre o bolero no México',
    'F3-03': 'URL trocada da página do repositório pelo PDF',
    'F4-02': 'capítulo curto (~330 palavras); complementa F4-01',
    'F7-03': 'resumo de sessão (~700 palavras), não o livro; o livro está na lista de compras',
}

# ---- NotebookLM: nada passou nos critérios
N = {
    'N1-02': 'processos composicionais de um compositor (Zé Barbeiro); o dossiê do choro (claude:F6-01) cobre o gênero',
    'N1-03': 'título genérico esconde dissertação sobre funk paulista — fora do tema (conferido no PDF)',
    'N1-04': 'política de patrimônio da viola em MG, sem descrição musical; Corrêa e Vilela cobrem',
}
def motivo_n(r):
    u = r['url'].lower()
    for k, m in [('scribd', 'cópia no Scribd (excluído por regra)'), ('dokumen.pub', 'cópia não autorizada (dokumen.pub)'),
                 ('archive.org/stream', 'livro comercial em cópia não autorizada'), ('academia.edu', 'Academia.edu bloqueia leitura'),
                 ('researchgate', 'ResearchGate bloqueia leitura (403)'), ('wikipedia', 'Wikipedia: não assinada'),
                 ('melodigging', 'agregador sem autoria'), ('flamencolive', 'catálogo comercial de loja')]:
        if k in u: return m
    return N.get(r['id'], 'fora dos critérios')

linhas, sel = [], []
def add(p, i, r, prio, nota):
    k = f'{p}:{i}'
    sel.append({'n': len(sel) + 1, 'origem': k, 'familia': r.get('familia', ''), 'aspectos': r.get('aspectos_cobertos', ''),
                'prioridade': prio, 'titulo': r['titulo'], 'autor': r.get('autor_instituicao', ''),
                'idioma': r.get('idioma', ''), 'tipo': r.get('tipo', ''), 'nivel': r.get('nivel', ''),
                'url': URL.get(k, r['url']), 'arquivo': ARQ.get(k, ''), 'nota': nota,
                'por_que': r.get('por_que_importa', '')})
    if 'pressbooks.pub' in sel[-1]['url']:
        sel[-1]['nota'] = (sel[-1]['nota'] + '; ' if sel[-1]['nota'] else '') + 'Pressbooks recusa leitor automático (CloudFront) — subir como arquivo, como na pesquisa 1'
    if 'openedition.org' in sel[-1]['url']:
        sel[-1]['nota'] = (sel[-1]['nota'] + '; ' if sel[-1]['nota'] else '') + 'OpenEdition mostra desafio anti-robô ao curl (o WebFetch leu o texto integral) — se o NotebookLM receber pouco texto, subir como arquivo'
    return len(sel)

for r in bruto:
    p, i = r['pesquisador'], r['id']
    if p == 'claude':
        d = C.get(i)
        if d: linhas.append((p, i, r['titulo'], r['url'], d[0], d[1])); continue
        n = add(p, i, r, PRIO_C.get(i, re.sub(r'\D', '', r.get('prioridade', '')) or '2'), NOTA_C.get(i, ''))
        linhas.append((p, i, r['titulo'], r['url'], 'incluir', f'selecionada #{n}'))
    elif p == 'chatgpt':
        d = G.get(i)
        if d and d[0] == 'dup': linhas.append((p, i, r['titulo'], r['url'], 'excluir', f'{DUP} {d[1]}'))
        elif d: linhas.append((p, i, r['titulo'], r['url'], d[0], d[1]))
        else:
            n = add(p, i, r, PRIO_G.get(i, re.sub(r'\D', '', r.get('prioridade', '')) or '2'), NOTA_G.get(i, ''))
            linhas.append((p, i, r['titulo'], r['url'], 'incluir', f'selecionada #{n}'))
    else:
        linhas.append((p, i, r['titulo'], r['url'], 'excluir', motivo_n(r)))

with open(B / 'decisao_por_fonte.csv', 'w', newline='') as f:
    w = csv.writer(f, delimiter=';'); w.writerow(['pesquisador', 'id', 'titulo', 'url', 'decisao', 'motivo']); w.writerows(linhas)
json.dump(sel, open(B / 'selecionadas.json', 'w'), ensure_ascii=False, indent=1)
from collections import Counter
print('linhas:', len(linhas), Counter(l[4] for l in linhas))
print('selecionadas:', len(sel), 'prioridade', sorted(Counter(s['prioridade'] for s in sel).items()))
print('por família', sorted(Counter(s['familia'] for s in sel).items(), key=lambda x: (len(x[0]), x[0])))
print('por origem', Counter(s['origem'].split(':')[0] for s in sel))
