# Para fontes que entraram só com a página de resumo: acha o PDF do texto integral
# (meta citation_pdf_url, link de download, arXiv abs->pdf) e baixa em 05_arquivos_enviados/.
import json, re, subprocess, sys, html, urllib.parse
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36'
def get(u, out):
    return subprocess.run(['curl', '-sL', '-m', '120', '-A', UA, '-o', out, '-w', '%{content_type}', u], capture_output=True, text=True).stdout
def palavras_pdf(f):
    return len(subprocess.run(['pdftotext', '-q', f, '-'], capture_output=True, text=True).stdout.split())
S = {s['n']: s for s in json.load(open('selecionadas.json'))}
res = {}
for n in map(int, sys.argv[1:]):
    u = S[n]['url']; dest = f'../05_arquivos_enviados/{n:03d}.pdf'
    cands = []
    m = re.search(r'arxiv\.org/abs/([\d.]+)', u)
    if m: cands.append(f'https://arxiv.org/pdf/{m.group(1)}')
    cands.append(u)
    got = None
    for c in cands:
        ct = get(c, '/tmp/_pag')
        if 'pdf' in ct: subprocess.run(['cp', '/tmp/_pag', dest]); got = c; break
        pag = open('/tmp/_pag', errors='ignore').read()
        links = re.findall(r'<meta[^>]+name="citation_pdf_url"[^>]+content="([^"]+)"', pag)
        links += [l for l in re.findall(r'href="([^"]+)"', pag) if re.search(r'\.pdf($|\?)|/download/|viewcontent\.cgi|/files/|/pdf/', l, re.I)]
        for l in links[:6]:
            l = urllib.parse.urljoin(c, html.unescape(l))
            if 'pdf' in get(l, dest): got = l; break
        if got: break
    w = palavras_pdf(dest) if got else 0
    res[n] = dict(url_pdf=got, arquivo=dest if got else None, palavras=w)
    print(n, w, got, flush=True)
json.dump(res, open(f'_achar_pdf_{sys.argv[1]}.json', 'w'), indent=1)
