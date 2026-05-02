#!/usr/bin/env python3
"""
Enriquece guias/<id>.md preenchendo síntese, conceitos, exercícios e sugestões
de leitura via LLM (Anthropic Haiku 4.5 ou OpenAI GPT-5-*).

Anti-invenção: o system prompt obriga "só fatos do texto, sem extrapolar".
Se a transcrição é omissa em algum ponto, o campo correspondente fica
explicitamente vazio com nota.

Uso:
  .venv/bin/python scripts/05_enrich_guias.py --item aula-001
  .venv/bin/python scripts/05_enrich_guias.py --batch 1
  .venv/bin/python scripts/05_enrich_guias.py --from 1 --to 40
  .venv/bin/python scripts/05_enrich_guias.py --all
  .venv/bin/python scripts/05_enrich_guias.py --stats

Provider:
  --provider anthropic   (default — claude-haiku-4-5; requer ANTHROPIC_API_KEY)
  --provider openai      (gpt-5-mini default; requer OPENAI_API_KEY)
  --model <id>           (override do modelo do provider escolhido)
"""
import argparse, json, re, sys, time, os, threading
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
try:
    import openai
except ImportError:
    openai = None

ROOT = Path(__file__).parent.parent
INV = ROOT / "plano/01_inventario_completo.json"
PROG = ROOT / "plano/_progresso.json"
GUIAS_DIR = ROOT / "guias"
LOT_SIZE = 20

DEFAULT_MODELS = {
    "anthropic": "claude-haiku-4-5",
    "openai": "gpt-5-mini",
}
MAX_CONTEXT_CHARS = 320_000  # ~80k tokens, deixa margem
MAX_OUTPUT_TOKENS = 16000  # folga p/ reasoning tokens (gpt-5-*) + JSON ~2k
OPENAI_REASONING_EFFORT = "minimal"  # extração direta; não precisa raciocínio

# Preços ($/Mtoken). Ajuste se a OpenAI publicar valores diferentes.
PRICES = {
    "claude-haiku-4-5":   {"in": 1.0,  "out": 5.0},
    "gpt-5-mini":         {"in": 0.25, "out": 2.0},
    "gpt-5-nano":         {"in": 0.05, "out": 0.4},
    "gpt-5":              {"in": 1.25, "out": 10.0},
}

SYSTEM_PROMPT = """Você é um assistente de curadoria pedagógica para o Curso \
Online de Filosofia (COF) de Olavo de Carvalho.

REGRA ABSOLUTA — ANTI-INVENÇÃO:
- Você responde EXCLUSIVAMENTE com base no texto da transcrição fornecida.
- Se uma informação não está no texto, você NÃO INVENTA — registra que não \
foi possível extrair.
- Você não traz conhecimento externo sobre Olavo, sobre os autores citados, \
nem sobre filosofia em geral. Apenas o que está no texto.
- Você não interpreta para além do texto. Se Olavo afirma X, você reproduz \
"Olavo afirma X". Você não diz "isso significa Y".
- Citações de autores: SOMENTE os que aparecem nominalmente na transcrição. \
Não invente "talvez Olavo esteja se referindo a...".

Saída SEMPRE em JSON válido com este schema exato:
{
  "sintese": "<até 300 palavras, redutor, fiel ao argumento central>",
  "conceitos_chave": [
    {"termo": "...", "definicao": "<definição funcional usada NESTA aula>"}
  ],
  "autores_obras_citados": [
    {"autor": "...", "obra": "<obra mencionada ou null>", "contexto": "<como aparece na aula>"}
  ],
  "sugestoes_leitura": [
    "<leitura sugerida explicitamente por Olavo, com obra e autor>"
  ],
  "conexoes_outras_aulas_cof": [
    "<remissão explícita: 'como vimos na aula NN' ou 'no curso X'>"
  ],
  "exercicios_fixacao": [
    {"tipo": "conceito|aplicacao|reflexao", "pergunta": "..."}
  ]
}

REGRAS DE PREENCHIMENTO:
- "conceitos_chave": 5 a 8 itens. Se o texto trouxer menos, listar quantos houver.
- "autores_obras_citados": apenas mencionados pelo nome no texto. Se não há \
autor identificável, lista vazia.
- "sugestoes_leitura": apenas se Olavo recomenda explicitamente. Se não \
recomenda, lista vazia.
- "conexoes_outras_aulas_cof": apenas remissões explícitas a outras aulas/cursos.
- "exercicios_fixacao": 3 a 5 exercícios. Mistura de tipos. Sem inventar fato \
ou usar conhecimento externo — exercícios devem testar o que ESTÁ na aula.

Se o texto for fragmento, transcrição parcial, ou estiver muito truncado para \
permitir síntese honesta, retorne JSON com campos vazios e explique no campo \
sintese (ex: "Texto insuficiente para síntese — apenas 800 palavras de cabeçalho").
"""


def load_inv():
    return json.loads(INV.read_text(encoding='utf-8'))

def load_prog():
    return json.loads(PROG.read_text(encoding='utf-8')) if PROG.exists() else {}

def save_prog(prog):
    PROG.write_text(json.dumps(prog, indent=2, ensure_ascii=False), encoding='utf-8')


# importa lógica de localização do body do script 04
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
m04 = import_module('04_generate_prompt_batch') if False else None
# fallback: implementar resolve_body local (independência)
def resolve_body(item):
    kind = item['kind']
    if kind == 'aula':
        for d in ('cof_remasterizado_transcricoes','cof_original_transcricoes'):
            p = ROOT/'_raw/dell_md'/d/item['file']
            if p.exists():
                txt = p.read_text(encoding='utf-8', errors='replace')
                return re.sub(r'^<!--.*?-->\n+','',txt,count=1,flags=re.DOTALL)
    elif kind == 'extra_aula':
        p = ROOT/'_raw/dell_md/extracurriculares'/item['file']
        if p.exists():
            text = p.read_text(encoding='utf-8', errors='replace')
            blocks = re.split(r'^---\n## FONTE:\s+(.+?)\n---\n', text, flags=re.MULTILINE)
            n = item['numero_interno']
            # 1) Match direto pelo numero_interno (funciona quando local==global)
            for i in range(1, len(blocks), 2):
                fname = blocks[i].strip()
                mm = re.search(r'Aula[_\s-](\d+)', fname) or re.match(r'^(\d+)', fname)
                if mm and int(mm.group(1)) == n:
                    return blocks[i+1] if i+1 < len(blocks) else ''
            # 2) Fallback: alguns extras têm numero_interno como índice global
            # acumulado (ex: 72-77 num curso de 6 aulas locais). Usar posição
            # relativa do item entre os do mesmo curso (rank ordenado).
            inv = load_inv()
            mesmos = sorted(
                [it for it in inv
                 if it.get('kind') == 'extra_aula'
                 and it.get('curso') == item.get('curso')],
                key=lambda it: it['numero_interno']
            )
            ids = [it['id'] for it in mesmos]
            if item['id'] in ids:
                rank = ids.index(item['id']) + 1
                for i in range(1, len(blocks), 2):
                    fname = blocks[i].strip()
                    mm = re.search(r'Aula[_\s-](\d+)', fname) or re.match(r'^(\d+)', fname)
                    if mm and int(mm.group(1)) == rank:
                        return blocks[i+1] if i+1 < len(blocks) else ''
    elif kind == 'livro':
        # Tenta primeiro nos diretórios do dell (63 livros do disco)
        for d in ('cof_original_livros','cof_remasterizado_livros'):
            p = ROOT/'_raw/dell_md'/d/item['file']
            if p.exists():
                txt = p.read_text(encoding='utf-8', errors='replace')
                return re.sub(r'^<!--.*?-->\n+','',txt,count=1,flags=re.DOTALL)
        # Fallback: 7 livros baixados do notebook ficam só em compiladas/livros/
        p = ROOT/'compiladas/livros'/item['file']
        if p.exists():
            txt = p.read_text(encoding='utf-8', errors='replace')
            return re.sub(r'^<!--.*?-->\n+','',txt,count=1,flags=re.DOTALL)
    elif kind in ('apostila','artigo','teoria_estado'):
        kind_to_file = {
            'apostila': '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Apostilas.md',
            'artigo':   '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Artigos.md',
            'teoria_estado': '_raw/tematicas_notebook/Aulas_Olavo_-_COF_-_Teoria_do_estado.md',
        }
        p = ROOT/kind_to_file[kind]
        if p.exists():
            return p.read_text(encoding='utf-8', errors='replace')
    return None


# Schema estrito para OpenAI Structured Outputs.
# Reproduz o schema do SYSTEM_PROMPT mas com tipagem enforced pela API.
OPENAI_SCHEMA = {
    "name": "guia_enriquecido",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": [
            "sintese", "conceitos_chave", "autores_obras_citados",
            "sugestoes_leitura", "conexoes_outras_aulas_cof", "exercicios_fixacao",
        ],
        "properties": {
            "sintese": {"type": "string"},
            "conceitos_chave": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["termo", "definicao"],
                    "properties": {
                        "termo": {"type": "string"},
                        "definicao": {"type": "string"},
                    },
                },
            },
            "autores_obras_citados": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["autor", "obra", "contexto"],
                    "properties": {
                        "autor": {"type": "string"},
                        "obra": {"type": ["string", "null"]},
                        "contexto": {"type": "string"},
                    },
                },
            },
            "sugestoes_leitura": {"type": "array", "items": {"type": "string"}},
            "conexoes_outras_aulas_cof": {"type": "array", "items": {"type": "string"}},
            "exercicios_fixacao": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["tipo", "pergunta"],
                    "properties": {
                        "tipo": {"type": "string", "enum": ["conceito", "aplicacao", "reflexao"]},
                        "pergunta": {"type": "string"},
                    },
                },
            },
        },
    },
}


def build_user_msg(body, item):
    body_truncated = body[:MAX_CONTEXT_CHARS]
    if len(body) > MAX_CONTEXT_CHARS:
        body_truncated += f"\n\n[NOTA: TEXTO TRUNCADO em {MAX_CONTEXT_CHARS} chars; total original: {len(body)} chars]"
    return f"""Item: {item.get('titulo','???')}
Categoria: {item.get('categoria','???')}
ID: {item['id']}

=== TRANSCRIÇÃO ===
{body_truncated}
=== FIM ===

Gere o JSON conforme o schema. Lembre-se: SOMENTE com base no texto acima.
"""


def call_anthropic(client, model, body, item):
    if not body:
        return None, "body vazio (não foi possível resolver fonte)"
    user_msg = build_user_msg(body, item)
    try:
        resp = client.messages.create(
            model=model,
            max_tokens=MAX_OUTPUT_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = resp.content[0].text
        m = re.search(r'\{[\s\S]*\}', text)
        if not m:
            return None, f"JSON não encontrado na resposta: {text[:200]}"
        data = json.loads(m.group())
        usage = {'input_tokens': resp.usage.input_tokens,
                 'output_tokens': resp.usage.output_tokens}
        return data, usage
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"
    except anthropic.APIError as e:
        return None, f"API error: {e}"
    except Exception as e:
        return None, f"erro: {e}"


def call_openai(client, model, body, item):
    if not body:
        return None, "body vazio (não foi possível resolver fonte)"
    user_msg = build_user_msg(body, item)
    kwargs = dict(
        model=model,
        max_completion_tokens=MAX_OUTPUT_TOKENS,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        response_format={"type": "json_schema", "json_schema": OPENAI_SCHEMA},
    )
    if model.startswith("gpt-5") or model.startswith("o"):
        kwargs["reasoning_effort"] = OPENAI_REASONING_EFFORT
    try:
        resp = client.chat.completions.create(**kwargs)
        choice = resp.choices[0]
        if choice.finish_reason not in ("stop", "length"):
            return None, f"finish_reason={choice.finish_reason}"
        text = choice.message.content
        if not text:
            return None, f"resposta vazia (finish_reason={choice.finish_reason})"
        data = json.loads(text)
        usage = {'input_tokens': resp.usage.prompt_tokens,
                 'output_tokens': resp.usage.completion_tokens}
        return data, usage
    except json.JSONDecodeError as e:
        return None, f"JSON inválido: {e}"
    except Exception as e:
        return None, f"erro: {e}"


def render_enriched_section(data):
    """Constrói o trecho do guia com as seções preenchidas."""
    lines = []
    lines.append("## Síntese\n")
    lines.append(data.get('sintese','*sem síntese gerada*').strip() + "\n")

    lines.append("## Conceitos-chave\n")
    for c in data.get('conceitos_chave', []):
        termo = c.get('termo','?')
        defi = c.get('definicao','?')
        lines.append(f"- **{termo}** — {defi}")
    if not data.get('conceitos_chave'):
        lines.append("*nenhum conceito extraído*")
    lines.append("")

    lines.append("## Autores e obras citadas\n")
    autores = data.get('autores_obras_citados', [])
    if autores:
        for a in autores:
            autor = a.get('autor','?')
            obra = a.get('obra')
            ctx = a.get('contexto','')
            obra_str = f" — *{obra}*" if obra else ""
            lines.append(f"- **{autor}**{obra_str} — {ctx}")
    else:
        lines.append("*nenhum autor identificado nominalmente nesta {kind}*")
    lines.append("")

    lines.append("## Sugestões de leitura\n")
    sugs = data.get('sugestoes_leitura', [])
    if sugs:
        for s in sugs:
            lines.append(f"- {s}")
    else:
        lines.append("*Olavo não fez recomendações explícitas de leitura nesta peça.*")
    lines.append("")

    lines.append("## Conexões com outras partes do COF\n")
    conex = data.get('conexoes_outras_aulas_cof', [])
    if conex:
        for c in conex:
            lines.append(f"- {c}")
    else:
        lines.append("*sem remissões explícitas a outras aulas/cursos.*")
    lines.append("")

    lines.append("## Exercícios de fixação\n")
    for i, ex in enumerate(data.get('exercicios_fixacao', []), 1):
        tipo = ex.get('tipo','?')
        perg = ex.get('pergunta','?')
        lines.append(f"{i}. *({tipo})* {perg}")
    if not data.get('exercicios_fixacao'):
        lines.append("*nenhum exercício gerado*")
    lines.append("")

    return "\n".join(lines)


def update_guia_file(item_id, enriched_section):
    """Substitui as seções placeholder do guia pelas seções enriquecidas."""
    guia_path = GUIAS_DIR / f"{item_id}.md"
    if not guia_path.exists():
        return False, "guia inexistente"
    text = guia_path.read_text(encoding='utf-8')
    # Substitui de "## Síntese" até "## Posição na trajetória" (preserva as
    # seções de header e a final).
    pattern = r'(## Síntese\n.*?)(?=## Posição na trajetória)'
    new_text, n = re.subn(pattern, enriched_section + "\n", text, count=1, flags=re.DOTALL)
    if n == 0:
        # backup-fallback: appendar
        new_text = text + "\n\n## (Enriquecimento)\n\n" + enriched_section
    guia_path.write_text(new_text, encoding='utf-8')
    return True, "ok"


def process(item, client, model, provider, dry_run=False):
    body = resolve_body(item)
    if not body:
        return 'no-body', None
    if provider == 'openai':
        data, usage_or_err = call_openai(client, model, body, item)
    else:
        data, usage_or_err = call_anthropic(client, model, body, item)
    if data is None:
        return 'error', usage_or_err
    if dry_run:
        return 'dry-run', usage_or_err
    enriched = render_enriched_section(data)
    ok, msg = update_guia_file(item['id'], enriched)
    return ('enriched' if ok else 'guia-error'), usage_or_err


def get_batch(items, n):
    start = (n-1) * LOT_SIZE
    return items[start:start+LOT_SIZE]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--item', type=str)
    g.add_argument('--batch', type=int)
    g.add_argument('--from', dest='lote_from', type=int)
    g.add_argument('--all', action='store_true')
    g.add_argument('--stats', action='store_true')
    ap.add_argument('--to', dest='lote_to', type=int)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--regenerate', action='store_true', help='reenriquecer mesmo se já enriched')
    ap.add_argument('--rps', type=float, default=2.0, help='requests/segundo (sequencial; ignorado se --workers>1)')
    ap.add_argument('--workers', type=int, default=1, help='paralelismo (default 1=sequencial)')
    ap.add_argument('--provider', choices=['anthropic', 'openai'], default='anthropic',
                    help='LLM backend (default anthropic)')
    ap.add_argument('--model', type=str, default=None,
                    help='override do modelo (default: claude-haiku-4-5 ou gpt-5-mini)')
    args = ap.parse_args()

    model = args.model or DEFAULT_MODELS[args.provider]

    items = load_inv()
    by_id = {it['id']: it for it in items}

    if args.stats:
        prog = load_prog()
        from collections import Counter
        c = Counter(prog.get(it['id'], {}).get('enrich_status','pending') for it in items)
        print(f"Total: {len(items)}")
        for s,n in sorted(c.items()):
            print(f"  {s}: {n}")
        return

    targets = []
    if args.item:
        if args.item not in by_id:
            print(f"ID não encontrado: {args.item}", file=sys.stderr); sys.exit(1)
        targets = [by_id[args.item]]
    elif args.batch:
        targets = get_batch(items, args.batch)
    elif args.lote_from:
        lt = args.lote_to or args.lote_from
        for n in range(args.lote_from, lt+1):
            targets.extend(get_batch(items, n))
    elif args.all:
        targets = items

    prog = load_prog()
    if not args.regenerate:
        targets = [it for it in targets
                   if prog.get(it['id'], {}).get('enrich_status') != 'enriched']
    print(f"Itens a processar: {len(targets)} | provider={args.provider} | model={model}")
    if not targets:
        return

    if args.provider == 'openai':
        if openai is None:
            print("openai package não instalado. Rode: .venv/bin/pip install openai", file=sys.stderr)
            sys.exit(2)
        if not os.environ.get('OPENAI_API_KEY'):
            print("OPENAI_API_KEY não está exportada no ambiente", file=sys.stderr)
            sys.exit(2)
        client = openai.OpenAI()
    else:
        client = anthropic.Anthropic()

    counts = {'enriched':0, 'no-body':0, 'error':0, 'dry-run':0, 'guia-error':0}
    total_in, total_out = 0, 0
    state_lock = threading.Lock()
    completed_n = [0]  # mutable counter para fechamento

    def handle_one(idx, it):
        t0 = time.time()
        status, usage_or_err = process(it, client, model, args.provider, dry_run=args.dry_run)
        elapsed = time.time() - t0
        with state_lock:
            counts[status] = counts.get(status, 0) + 1
            nonlocal_in, nonlocal_out = 0, 0
            if isinstance(usage_or_err, dict):
                nonlocal_in = usage_or_err.get('input_tokens', 0)
                nonlocal_out = usage_or_err.get('output_tokens', 0)
            if not args.dry_run:
                prog[it['id']] = {
                    **prog.get(it['id'], {}),
                    'enrich_status': status if status=='enriched' else f'error:{status}',
                    'enrich_updated_at': datetime.now().isoformat(),
                    'enrich_input_tokens': usage_or_err.get('input_tokens') if isinstance(usage_or_err, dict) else None,
                    'enrich_output_tokens': usage_or_err.get('output_tokens') if isinstance(usage_or_err, dict) else None,
                }
                completed_n[0] += 1
                if completed_n[0] % 10 == 0:
                    save_prog(prog)
        msg = f"  [{idx:3d}/{len(targets)}] {it['id']:55s} {status:12s} ({elapsed:.1f}s)"
        if status == 'error':
            msg += f"  err={str(usage_or_err)[:80]}"
        print(msg, flush=True)
        return nonlocal_in, nonlocal_out

    if args.workers > 1:
        with ThreadPoolExecutor(max_workers=args.workers) as ex:
            futures = {ex.submit(handle_one, i+1, it): it for i, it in enumerate(targets)}
            for f in as_completed(futures):
                try:
                    tin, tout = f.result()
                    total_in += tin
                    total_out += tout
                except Exception as e:
                    print(f"  [thread err] {e}", flush=True)
    else:
        delay = 1.0 / args.rps if args.rps > 0 else 0
        for i, it in enumerate(targets, 1):
            t0 = time.time()
            tin, tout = handle_one(i, it)
            total_in += tin
            total_out += tout
            elapsed = time.time() - t0
            if delay > 0 and i < len(targets):
                time.sleep(max(0, delay - elapsed))

    if not args.dry_run:
        save_prog(prog)

    price = PRICES.get(model, {"in": 0, "out": 0})
    cost = total_in/1e6 * price["in"] + total_out/1e6 * price["out"]
    print(f"\nResumo: {counts}")
    print(f"Tokens: {total_in:,} in + {total_out:,} out → ~${cost:.2f} ({model})")


if __name__ == "__main__":
    main()
