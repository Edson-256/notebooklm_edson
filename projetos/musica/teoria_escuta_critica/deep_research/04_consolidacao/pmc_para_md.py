# Baixa o texto integral de um artigo PMC pela API aberta da Europe PMC e grava como .md
# (o NotebookLM recebe captcha do site do PMC). Uso: pmc_para_md.py PMC1234567 saida.md "Título"
import sys, re, urllib.request, xml.etree.ElementTree as ET
pmc, saida, titulo = sys.argv[1], sys.argv[2], sys.argv[3]
try:
    xml = urllib.request.urlopen(f'https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML', timeout=60).read()
except Exception:  # Europe PMC instável (502/503): cai para a E-utilities do NCBI
    xml = urllib.request.urlopen(f'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id={pmc[3:]}&rettype=xml', timeout=60).read()
root = ET.fromstring(xml)
def txt(e): return re.sub(r'\s+', ' ', ''.join(e.itertext())).strip()
out = [f'# {titulo}', '', f'Fonte: https://pmc.ncbi.nlm.nih.gov/articles/{pmc}/ (texto integral via Europe PMC / NCBI)', '']
ab = root.find('.//abstract')
if ab is not None: out += ['## Abstract', '', txt(ab), '']
body = root.find('.//body')
def walk(e, nivel=2):
    for c in e:
        if c.tag == 'sec':
            t = c.find('title')
            if t is not None: out.extend(['#' * min(nivel, 6) + ' ' + txt(t), ''])
            walk(c, nivel + 1)
        elif c.tag == 'p': out.extend([txt(c), ''])
        elif c.tag in ('list', 'disp-quote', 'table-wrap', 'fig'):
            s = txt(c)
            if s: out.extend([s, ''])
if body is not None: walk(body)
open(saida, 'w').write('\n'.join(out))
print(pmc, len(' '.join(out).split()), 'palavras')
