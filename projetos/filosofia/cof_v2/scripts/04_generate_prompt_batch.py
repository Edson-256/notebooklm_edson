#!/usr/bin/env python3
"""
Gera prompts e guias de aula para itens do plano COF v2, em lotes de 20.

Saída:
  prompts/<item_id>.md   — prompt pronto para `nlm audio create`
  guias/<item_id>.md     — guia .md do estudante

Tracking:
  plano/_progresso.json  — status por item (pending|prepared|sent|done|error)

Uso típico:
  python3 scripts/04_generate_prompt_batch.py --list
  python3 scripts/04_generate_prompt_batch.py --batch 1
  python3 scripts/04_generate_prompt_batch.py --batch 1 --dry-run
  python3 scripts/04_generate_prompt_batch.py --from 1 --to 5
  python3 scripts/04_generate_prompt_batch.py --item aula-001
  python3 scripts/04_generate_prompt_batch.py --item aula-001 --regenerate
  python3 scripts/04_generate_prompt_batch.py --stats
"""
import argparse, json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict

ROOT = Path(__file__).parent.parent
INV = ROOT / "plano/01_inventario_completo.json"
PROG = ROOT / "plano/_progresso.json"
PROMPTS_DIR = ROOT / "prompts"
GUIAS_DIR = ROOT / "guias"

LOT_SIZE = 20
WORDS_TARGET_DURATION = {  # estimativa de duração por formato
    'Deep Dive': '25–35 min',
    'The Brief': '8–12 min',
    'The Critique': '15–25 min',
    'The Debate': '20–30 min',
}

MONTHS_PT = ['janeiro','fevereiro','março','abril','maio','junho',
             'julho','agosto','setembro','outubro','novembro','dezembro']

def fmt_date(iso):
    if not iso: return None
    try:
        y,m,d = iso.split('-')
        return f"{int(d)} de {MONTHS_PT[int(m)-1]} de {y}"
    except Exception:
        return iso


# ── Carregar/salvar estado ────────────────────────────────────────────
def load_inv():
    return json.loads(INV.read_text(encoding='utf-8'))

def load_prog():
    if not PROG.exists():
        return {}
    return json.loads(PROG.read_text(encoding='utf-8'))

def save_prog(prog):
    PROG.write_text(json.dumps(prog, indent=2, ensure_ascii=False), encoding='utf-8')


# ── Localizar conteúdo de um item ─────────────────────────────────────
def resolve_body(item):
    """Lê o markdown da fonte e retorna o body (sem headers). None se não encontrar."""
    kind = item['kind']
    if kind == 'aula':
        for d in ('cof_remasterizado_transcricoes','cof_original_transcricoes'):
            p = ROOT / '_raw/dell_md' / d / item['file']
            if p.exists():
                txt = p.read_text(encoding='utf-8', errors='replace')
                return re.sub(r'^<!--.*?-->\n+','',txt,count=1,flags=re.DOTALL)
    elif kind == 'extra_aula':
        # ler bloco específico do Unif_
        p = ROOT / '_raw/dell_md/extracurriculares' / item['file']
        if p.exists():
            text = p.read_text(encoding='utf-8', errors='replace')
            blocks = re.split(r'^---\n## FONTE:\s+(.+?)\n---\n', text, flags=re.MULTILINE)
            n = item['numero_interno']
            for i in range(1, len(blocks), 2):
                fname = blocks[i].strip()
                m = re.match(r'^(\d+)', fname)
                if m and int(m.group(1)) == n:
                    return blocks[i+1] if i+1 < len(blocks) else ''
    elif kind == 'livro':
        for d in ('cof_original_livros','cof_remasterizado_livros'):
            p = ROOT / '_raw/dell_md' / d / item['file']
            if p.exists():
                txt = p.read_text(encoding='utf-8', errors='replace')
                return re.sub(r'^<!--.*?-->\n+','',txt,count=1,flags=re.DOTALL)
        # fallback: compiladas/livros
        for p in (ROOT/'compiladas/livros').glob('*.md'):
            if p.stem.lower().startswith(item['titulo'][:30].lower()):
                return p.read_text(encoding='utf-8', errors='replace')
    elif kind in ('apostila','artigo','teoria_estado'):
        # body já foi fragmentado mas não preservado individualmente; reler do
        # arquivo temático e localizar pelo título do item
        kind_to_file = {
            'apostila': '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Apostilas.md',
            'artigo':   '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Artigos.md',
            'teoria_estado': '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Teoria_do_estado.md',
        }
        p = ROOT / kind_to_file[kind]
        if p.exists():
            return p.read_text(encoding='utf-8', errors='replace')
    return None


# ── Extrair features (autores citados, conceitos) ─────────────────────
AUTORES_RE = re.compile(
    r'\b('
    r'Aristóteles|Aristoteles|Plat[ãa]o|S[ôo]crates|Voegelin|'
    r'Lavelle|Bergson|Husserl|Heidegger|Kant|Hegel|Marx|Nietzsche|'
    r'M[áa]rio Ferreira(?: dos Santos)?|Olavo|Tom[áa]s de Aquino|'
    r'Santo Agostinho|Descartes|Locke|Hume|Espinosa|Spinoza|'
    r'Schopenhauer|Berdyaev|Soloviev|Florensky|Bulgakov|'
    r'Maritain|Gilson|Pieper|Guénon|Coomaraswamy|Schuon|'
    r'Eric Voegelin|Louis Lavelle|Bernanos|Dostoiévski|Tolst[óo]i|'
    r'Goethe|Shakespeare|Dante|Homero|Vergil|Horácio|'
    r'Bertrand Russell|Wittgenstein|Popper|Frege|G[öo]del|'
    r'Roger Scruton|Russell Kirk|Eric Hoffer|Strauss|Voegelin'
    r')\b'
)

def extract_authors(body, max_n=10):
    if not body: return []
    found = set()
    for m in AUTORES_RE.finditer(body):
        found.add(m.group(1))
    return sorted(found)[:max_n]


# ── Templates ─────────────────────────────────────────────────────────
SKIP_LINE_RE = re.compile(
    r'(VERSÃO PROVISÓRIA|Para uso exclusivo|Curso de Filosofia Online|'
    r'O texto desta transcri[çc][ãa]o|n[ãa]o foi revisto|Olavo de Carvalho|'
    r'^Aula\s+\d+\s*$|de \w+ de \d{4}\s*$|Boa (tarde|noite) a todos|'
    r'Sejam bem-vindos|Title:|Author:|Por Olavo)', re.IGNORECASE)

def gancho(prox_body):
    """1ª frase substancial do body da próxima aula → gancho."""
    if not prox_body: return None
    # remover boilerplate frequente
    cleaned = "\n".join(l for l in prox_body[:6000].splitlines()
                        if l.strip() and not SKIP_LINE_RE.search(l))
    for sent in re.split(r'(?<=[.!?])\s+', cleaned):
        sent = sent.strip()
        # pular cabeçalhos, datas isoladas, marcadores
        if 50 < len(sent) < 250 and not sent.startswith(('#','*','---','<!--','[','Title:','Author:')):
            return sent.replace('\n',' ')
    return cleaned[:200].strip().replace('\n',' ')


def render_prompt(item, all_items_by_id, body=None):
    kind_h = {
        'aula': 'aula',
        'extra_aula': 'aula do curso',
        'livro': 'livro',
        'apostila': 'apostila',
        'artigo': 'artigo',
        'teoria_estado': 'aula do curso Teoria do Estado',
    }[item['kind']]

    if item['kind'] == 'aula':
        n = item.get('numero_aula', 0)
        num_h = f"número {n:03d}" if isinstance(n, int) else f"número {n}"
    elif item['kind'] == 'extra_aula':
        n = item.get('numero_interno', 0)
        ns = f"{n:02d}" if isinstance(n, int) else str(n)
        num_h = f"número {ns} do curso “{item.get('curso','')}”"
    else:
        num_h = f"“{item.get('titulo','')}”"

    data_h = fmt_date(item.get('data')) if item['kind']=='aula' and item.get('data') else None
    data_clause = f"apresentada em {data_h}." if data_h else ""

    prev = all_items_by_id.get(item.get('anterior'))
    prox = all_items_by_id.get(item.get('proxima'))
    prev_body = resolve_body(prev) if prev else None  # fica caro; usar lazy
    prox_body = resolve_body(prox) if prox else None
    prox_gancho = gancho(prox_body) if prox_body else ''

    intro = ""
    if prev:
        prev_data = fmt_date(prev.get('data')) if prev.get('data') else ''
        intro = (f"Antes de entrar no conteúdo de hoje, lembre brevemente o que "
                 f"foi visto na {kind_h} anterior — \"{prev.get('titulo','')[:80]}\""
                 + (f" ({prev_data})" if prev_data else "") + ". "
                 "Reative o fio condutor: a partir de onde o pensamento estava, "
                 "para onde caminhamos hoje. NÃO resuma o anterior em detalhe — "
                 "só recoloque o ouvinte no ponto da formação.")
    else:
        intro = (f"Esta é a primeira {kind_h} da série na sua categoria "
                 f"({item['categoria']}). Apresente brevemente o cenário geral "
                 f"do COF e o que torna esta {kind_h} um ponto de partida natural.")

    desenv = {
        'Deep Dive': (
            "- Análise detalhada dos pontos-chave.\n"
            "- Para cada conceito central: definição funcional, exemplo, "
            "implicação prática, eventual digressão pertinente.\n"
            "- Preserve as imagens e exemplos do próprio Olavo (são pedagógicos).\n"
            "- Demonstre o encadeamento argumentativo, não só o resultado."
        ),
        'The Brief': (
            "- Sumário executivo: tese central + 3–5 pontos de apoio.\n"
            "- Linguagem direta, sem digressões.\n"
            "- Foco no \"o quê\" e no \"por que importa\", não no \"como se prova\"."
        ),
        'The Critique': (
            "- Apresente honestamente a posição que está sendo criticada antes "
            "de reproduzir a crítica de Olavo.\n"
            "- Distinga: o que Olavo mostra ser falso, o que ele mostra ser "
            "confuso, o que ele mostra ser perigoso.\n"
            "- Termine com o que fica de pé depois da crítica (não só "
            "destruição)."
        ),
        'The Debate': (
            "- Apresente as posições legítimas em jogo (não só a de Olavo).\n"
            "- Mostre os argumentos mais fortes de cada lado.\n"
            "- Posicione Olavo como uma das vozes — a mais relevante para o COF "
            "— sem reduzir o tema à sua resposta."
        ),
    }[item['formato_audio']]

    outro = ""
    if prox:
        prox_data = fmt_date(prox.get('data')) if prox.get('data') else ''
        outro = (f"Antes de fechar, anuncie a continuidade: na {kind_h} a seguir "
                 f"— \"{prox.get('titulo','')[:80]}\""
                 + (f" ({prox_data})" if prox_data else "") + " — avançaremos. "
                 + (f"Pista do que vem: \"{prox_gancho[:200]}\". "
                    if prox_gancho else "")
                 + f"Deixe uma pergunta aberta que ligue esta {kind_h} à próxima.")
    else:
        outro = (f"Esta é a última {kind_h} da série em sua categoria. Faça um "
                 "fechamento que situe o conteúdo na obra do Olavo como um todo.")

    duracao = WORDS_TARGET_DURATION.get(item['formato_audio'], '15–25 min')

    prompt = f"""[ID]: {item['id']}
[CATEGORIA]: {item['categoria']}
[FORMATO]: {item['formato_audio']}
[POSIÇÃO MESTRA]: {item['seq_global']}/{len(all_items_by_id)}
[ANTERIOR]: {item.get('anterior') or '— (primeira da categoria)'}
[PRÓXIMA]: {item.get('proxima') or '— (última da categoria)'}

INSTRUÇÕES PARA O ÁUDIO

ORIGEM E IDENTIFICAÇÃO
Este áudio integra a série didática do Curso Online de Filosofia (COF) de
Olavo de Carvalho. Ao iniciar, anuncie:
"Esta é a {kind_h} {num_h} do COF{', ' + data_clause if data_clause else ''}"

OBJETIVO PEDAGÓGICO
Tornar o conteúdo filosófico denso desta {kind_h} acessível ao ouvinte sem
perder rigor. Trate o ouvinte como estudante interessado mas não-especialista.
Filosofia é responsabilidade total — preserve essa serenidade.

INTRODUÇÃO SEQUENCIAL (1–2 minutos)
{intro}

DESENVOLVIMENTO ({duracao})
Aplique rigorosamente o formato **{item['formato_audio']}**:
{desenv}

ESCOPO ESTRITO
Use apenas o conteúdo desta {kind_h}. NÃO inclua material de outras aulas
além de referências breves para continuidade. NÃO improvise contexto.
Se a fonte é omissa em algum ponto, diga "este ponto é tratado em outra aula"
e siga.

ENCERRAMENTO SEQUENCIAL (~30 segundos)
{outro}

LINGUAGEM E TOM
Português brasileiro. Didático mas adulto. Fiel ao rigor do COF. Termo técnico
sempre definido na 1ª aparição.
"""
    return prompt


def render_guia(item, all_items_by_id, body):
    autores = extract_authors(body or '', max_n=10) if body else []
    autores_md = "\n".join(f"- **{a}** — citado nesta {item['kind'].replace('_',' ')}." for a in autores) \
                  if autores else "- *(sem autores reconhecidos pela heurística automática; revisar manualmente)*"

    prev = all_items_by_id.get(item.get('anterior'))
    prox = all_items_by_id.get(item.get('proxima'))

    prev_link = f"[[{prev['id']}]] — {prev.get('titulo','')[:60]}" if prev else "*(primeiro da categoria)*"
    prox_link = f"[[{prox['id']}]] — {prox.get('titulo','')[:60]}" if prox else "*(último da categoria)*"

    data_h = fmt_date(item.get('data')) if item.get('data') else None

    guia = f"""# Guia — {item.get('titulo','???')}

**ID:** `{item['id']}`
**Categoria:** {item['categoria']}
**Formato do áudio:** {item['formato_audio']} (motivo: {item.get('formato_razao','')})
{f'**Data original:** {data_h}' if data_h else ''}
**Posição mestra:** {item['seq_global']}/{len(all_items_by_id)}
**Anterior:** {prev_link}
**Próxima:** {prox_link}

## Síntese

*A preencher após gerar o áudio (síntese fiel ao conteúdo, máx. 300 palavras).*

## Conceitos-chave

*5–8 conceitos centrais com definição funcional dentro do contexto. A preencher
após análise do áudio gerado.*

## Autores e obras citadas

{autores_md}

> ⚠️ **Apenas autores realmente mencionados.** Se a heurística não detectou
> autor que de fato aparece, complemente manualmente lendo a fonte. Se a
> heurística trouxe falso-positivo, remova.

## Sugestões de leitura

*Derivadas das obras citadas acima. Preferência por edições em português ou
indicadas pelo próprio Olavo. A preencher.*

## Conexões com outras partes do COF

*Apenas remissões explícitas. A preencher se Olavo cita outra aula/curso.*

## Exercícios de fixação

1. *(conceito)* …
2. *(aplicação)* …
3. *(reflexão pessoal)* …

## Posição na trajetória

*Como esta {item['kind'].replace('_',' ')} se conecta com {prev_link} e
prepara {prox_link}. Parágrafo curto — a preencher depois do áudio.*

---

*Guia gerado em {datetime.now().strftime('%Y-%m-%d %H:%M')} pelo
`scripts/04_generate_prompt_batch.py`. Conteúdo vazio é proposital
— a IA preenche após gerar e ouvir o áudio. Curadoria humana antes
do uso pedagógico.*
"""
    return guia


# ── Processamento ─────────────────────────────────────────────────────
def process_item(item, all_items_by_id, dry_run=False, regenerate=False):
    p_path = PROMPTS_DIR / f"{item['id']}.md"
    g_path = GUIAS_DIR / f"{item['id']}.md"
    if p_path.exists() and g_path.exists() and not regenerate:
        return 'skipped'
    body = resolve_body(item)
    prompt = render_prompt(item, all_items_by_id, body)
    guia = render_guia(item, all_items_by_id, body)
    if dry_run:
        return 'dry-run'
    PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
    GUIAS_DIR.mkdir(parents=True, exist_ok=True)
    p_path.write_text(prompt, encoding='utf-8')
    g_path.write_text(guia, encoding='utf-8')
    return 'prepared'


def get_batch(items, n):
    """Retorna o lote N (1-indexed)."""
    start = (n-1) * LOT_SIZE
    return items[start:start+LOT_SIZE]


def cmd_list(items):
    prog = load_prog()
    n_lotes = -(-len(items)//LOT_SIZE)
    print(f"Total: {len(items)} itens em {n_lotes} lotes de {LOT_SIZE}\n")
    print(f"{'Lote':>4} | {'Itens':>5} | {'Pendentes':>9} | {'Preparados':>10} | Categorias")
    print("-"*100)
    for i in range(1, n_lotes+1):
        batch = get_batch(items, i)
        pend = sum(1 for it in batch if prog.get(it['id'], {}).get('status','pending')=='pending')
        prep = sum(1 for it in batch if prog.get(it['id'], {}).get('status') in ('prepared','sent','done'))
        from collections import Counter
        cats = Counter(it['categoria'] for it in batch)
        cats_str = ', '.join(f"{c}({n})" for c,n in cats.most_common(2))
        print(f"  {i:02d} | {len(batch):>5d} | {pend:>9d} | {prep:>10d} | {cats_str}")


def cmd_stats(items):
    prog = load_prog()
    from collections import Counter
    statuses = Counter(prog.get(it['id'], {}).get('status','pending') for it in items)
    print(f"Total de itens: {len(items)}")
    for s, n in sorted(statuses.items()):
        print(f"  {s:12s}: {n:4d}")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--batch', type=int, help='Roda lote N (1..N_TOTAL)')
    g.add_argument('--from', dest='lote_from', type=int)
    g.add_argument('--item', type=str, help='Roda 1 item específico (ID)')
    g.add_argument('--list', action='store_true', help='Lista lotes com status')
    g.add_argument('--stats', action='store_true', help='Mostra progresso')
    ap.add_argument('--to', dest='lote_to', type=int, help='(usar com --from) lote final inclusivo')
    ap.add_argument('--dry-run', action='store_true', help='Não escreve arquivos')
    ap.add_argument('--regenerate', action='store_true', help='Sobrescreve existentes')
    args = ap.parse_args()

    items = load_inv()
    by_id = {it['id']: it for it in items}

    if args.list:
        cmd_list(items)
        return
    if args.stats:
        cmd_stats(items)
        return

    targets = []
    if args.batch:
        targets = get_batch(items, args.batch)
        print(f"Lote {args.batch}: {len(targets)} itens")
    elif args.lote_from:
        lf = args.lote_from
        lt = args.lote_to or args.lote_from
        for n in range(lf, lt+1):
            targets.extend(get_batch(items, n))
        print(f"Lotes {lf}–{lt}: {len(targets)} itens")
    elif args.item:
        if args.item not in by_id:
            print(f"ID não encontrado: {args.item}", file=sys.stderr)
            sys.exit(1)
        targets = [by_id[args.item]]

    prog = load_prog()
    counts = defaultdict(int)
    for i, it in enumerate(targets, 1):
        try:
            status = process_item(it, by_id, dry_run=args.dry_run, regenerate=args.regenerate)
        except Exception as e:
            status = f"error:{e}"
        counts[status.split(':')[0]] += 1
        if not args.dry_run:
            prog[it['id']] = {
                'status': 'prepared' if status=='prepared' else
                          ('skipped' if status=='skipped' else 'error'),
                'updated_at': datetime.now().isoformat(),
            }
        line = f"  [{i:3d}/{len(targets)}] {it['id']:50s} {status}"
        print(line)
    if not args.dry_run:
        save_prog(prog)
    print(f"\nResumo: {dict(counts)}")
    if not args.dry_run:
        print(f"Progresso salvo em {PROG.name}")


if __name__ == "__main__":
    main()
