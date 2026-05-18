#!/usr/bin/env python3
"""
Define a fila master de cenas a partir dos 1364 capítulos em obras/*/capitulos/.

Cada capítulo vira 1 cena (caso curto) ou várias sub-cenas (caso longo > 8000 chars,
limite prático do NotebookLM para Audio Overview de ~12-18min).

A fila é ordenada por priority_rank (canônica — ver docs/priority_order.md), depois
por livro/capítulo/sub-cena.

Output: _raw/cenas_master.json — consumido pelo 05_daily_cenas_runner.py.

Uso:
  python scripts/04_define_cenas_master.py            # gera o master
  python scripts/04_define_cenas_master.py --dry-run  # apenas mostra estatísticas
  python scripts/04_define_cenas_master.py --force    # sobrescreve preservando status

A flag --force MERGE: mantém o status (done/failed) de cenas que já existiam,
apenas atualiza estrutura. Use quando regenerar após adicionar/corrigir capítulos.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CAPITULOS_GLOB = "obras/*/*/capitulos/*.md"
MASTER_PATH = PROJECT_ROOT / "_raw" / "cenas_master.json"

MAX_CHARS_PER_CENA = 8000   # ~2k palavras ~12-18min de áudio NLM
MIN_CHARS_TO_SPLIT = 12000  # só divide se justifica (não criar muitas sub-cenas curtas)


# Ordem canônica do Corpus Aristotelicum (Bekker) — usada para o número
# da obra no nome de arquivo do áudio (aristoteles_NN_...). Reflete a ordem
# de upload no notebook 'Aristóteles (completo)'.
# Chave: (categoria, obra_slug) → idx da obra (1-33).
# Para Parva Naturalia (7 sub-obras compartilhando obra_slug), uso um sub-mapping
# por capitulo_path para distinguir.
CANONICAL_OBRA_IDX: dict[tuple[str, str], int] = {
    ("01_organon", "01_categorias"): 1,
    ("01_organon", "02_da_interpretacao"): 2,
    ("01_organon", "03_analiticos_anteriores"): 3,
    ("01_organon", "04_analiticos_posteriores"): 4,
    ("01_organon", "05_topicos"): 5,
    ("01_organon", "06_refutacoes_sofisticas"): 6,
    ("02_fisica", "01_fisica"): 7,
    ("02_fisica", "02_sobre_o_ceu"): 8,
    ("02_fisica", "03_geracao_corrupcao"): 9,
    ("02_fisica", "04_meteorologia"): 10,
    ("03_psicologia_biologia", "01_de_anima"): 11,
    # 12-18: Parva Naturalia (resolvido por sub_slug abaixo)
    ("03_psicologia_biologia", "03_historia_animais"): 19,
    ("03_psicologia_biologia", "04_partes_animais"): 20,
    ("03_psicologia_biologia", "05_movimento_animais"): 21,
    ("03_psicologia_biologia", "06_marcha_animais"): 22,
    ("03_psicologia_biologia", "07_geracao_animais"): 23,
    ("04_metafisica", "01_metafisica"): 24,
    ("05_etica", "01_etica_nicomaco"): 25,
    ("05_etica", "02_etica_eudemo"): 26,
    # 27-28: Magna Moralia + Virtues (compartilham obra_slug — resolvidos por sub_slug)
    ("06_politica", "01_politica"): 29,
    ("06_politica", "02_constituicao_atenienses"): 30,
    ("06_politica", "03_economicos"): 31,
    ("07_retorica_poetica", "01_retorica"): 32,
    ("07_retorica_poetica", "02_poetica"): 33,
}

# Para diretórios compartilhados, mapear sub_slug (prefixo do nome do arquivo) → obra_idx.
SUB_OBRA_IDX: dict[str, int] = {
    # Parva Naturalia (12-18)
    "on_sense_and_the_sensible": 12,
    "on_memory_and_reminiscence": 13,
    "on_sleep_and_sleeplessness": 14,
    "on_dreams": 15,
    "on_prophesying_by_dreams": 16,
    "on_longevity_and_shortness_of_life": 17,
    "on_youth_and_old_age_on_life_and_death_on_breathing": 18,
    # Magna Moralia compartilhado (27-28)
    "magna_moralia": 27,
    "on_virtues_and_vices": 28,
}


# Ordem canônica das obras (priority_rank menor = maior prioridade).
# Tier definido em docs/priority_order.md. Chave: (categoria, obra_slug).
# Se uma obra não estiver listada, recebe rank alto (no fim).
PRIORITY_ORDER: list[tuple[str, str]] = [
    # Tier 1 — Prática
    ("05_etica", "01_etica_nicomaco"),
    ("06_politica", "01_politica"),
    ("07_retorica_poetica", "02_poetica"),
    ("07_retorica_poetica", "01_retorica"),
    # Tier 2 — Filosofia primeira
    ("04_metafisica", "01_metafisica"),
    ("03_psicologia_biologia", "01_de_anima"),
    # Tier 3 — Lógica
    ("01_organon", "01_categorias"),
    ("01_organon", "02_da_interpretacao"),
    ("01_organon", "04_analiticos_posteriores"),
    ("01_organon", "03_analiticos_anteriores"),
    # Tier 4 — Filosofia natural
    ("02_fisica", "01_fisica"),
    ("02_fisica", "02_sobre_o_ceu"),
    ("02_fisica", "03_geracao_corrupcao"),
    ("02_fisica", "04_meteorologia"),
    # Tier 5 — Dialética
    ("01_organon", "05_topicos"),
    ("01_organon", "06_refutacoes_sofisticas"),
    # Tier 6 — Biologia
    ("03_psicologia_biologia", "04_partes_animais"),
    ("03_psicologia_biologia", "03_historia_animais"),
    ("03_psicologia_biologia", "05_movimento_animais"),
    ("03_psicologia_biologia", "06_marcha_animais"),
    ("03_psicologia_biologia", "07_geracao_animais"),
    # Tier 7 — Parva Naturalia
    ("03_psicologia_biologia", "02_parva_naturalia"),
    # Tier 8 — Atribuídas/históricas
    ("06_politica", "02_constituicao_atenienses"),
    ("05_etica", "02_etica_eudemo"),
    ("05_etica", "03_magna_moralia"),
    ("06_politica", "03_economicos"),
]


def get_priority_rank(categoria: str, obra_slug: str) -> int:
    key = (categoria, obra_slug)
    try:
        return PRIORITY_ORDER.index(key) + 1
    except ValueError:
        return 999  # obras sem rank vão para o fim


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extrai frontmatter YAML simples (k: v por linha) + corpo."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    fm_text = text[4:end]
    body = text[end + 5:].lstrip("\n")
    fm: dict = {}
    for ln in fm_text.splitlines():
        if ":" not in ln:
            continue
        k, _, v = ln.partition(":")
        v = v.strip()
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        if v.isdigit():
            v = int(v)
        fm[k.strip()] = v
    return fm, body


def split_into_subcenas(body: str) -> list[str]:
    """Divide o corpo em sub-cenas preservando parágrafos."""
    if len(body) <= MIN_CHARS_TO_SPLIT:
        return [body]
    paragraphs = re.split(r"\n\s*\n", body)
    chunks: list[list[str]] = []
    current: list[str] = []
    current_size = 0
    for p in paragraphs:
        p_size = len(p) + 2
        if current_size + p_size > MAX_CHARS_PER_CENA and current:
            chunks.append(current)
            current = [p]
            current_size = p_size
        else:
            current.append(p)
            current_size += p_size
    if current:
        chunks.append(current)
    return ["\n\n".join(c).strip() + "\n" for c in chunks]


def first_sentence(text: str, max_len: int = 200) -> str:
    """Primeira frase (até ponto final ou max_len)."""
    text = text.strip()
    m = re.search(r"^(.{20,}?[\.\?!])\s", text)
    if m:
        s = m.group(1)
    else:
        s = text[:max_len]
    return re.sub(r"\s+", " ", s).strip()[:max_len]


def last_sentence(text: str, max_len: int = 200) -> str:
    text = text.rstrip()
    # pega últimas ~300 chars e procura a última frase
    tail = text[-500:]
    matches = re.findall(r"([^\.\?!]{20,}?[\.\?!])(?=\s|$)", tail)
    if matches:
        s = matches[-1]
    else:
        s = tail[-max_len:]
    return re.sub(r"\s+", " ", s).strip()[:max_len]


def resolve_obra_idx(categoria: str, obra_slug: str, base_filename: str) -> int:
    """Devolve o índice canônico (1-33) da obra correspondente.
    Trata diretórios compartilhados (Parva Naturalia, Magna+Virtues) via sub_slug."""
    # Caso simples: obra única no dir
    if (categoria, obra_slug) in CANONICAL_OBRA_IDX:
        return CANONICAL_OBRA_IDX[(categoria, obra_slug)]
    # Caso compartilhado: sub_slug é prefixo do filename
    for sub_slug, idx in SUB_OBRA_IDX.items():
        if base_filename.startswith(sub_slug + "-"):
            return idx
    return 99  # desconhecido — usar slot alto


def build_audio_filename(obra_idx: int, livro_num: int, capitulo_num: int,
                         sub_cena_num: int, slug_obra: str) -> str:
    """Nome de arquivo canônico para o áudio gerado.
    Ex: 'aristoteles_25_l01_c01_cena01_nicomachean_ethics.m4a'."""
    return (f"aristoteles_{obra_idx:02d}_l{livro_num:02d}_"
            f"c{capitulo_num:02d}_cena{sub_cena_num:02d}_{slug_obra}.m4a")


def collect_capitulos() -> list[dict]:
    """Percorre todos os .md em obras/*/*/capitulos/ e devolve list de cenas
    já expandidas em sub-cenas."""
    cenas: list[dict] = []
    paths = sorted(PROJECT_ROOT.glob(CAPITULOS_GLOB))
    for cap_path in paths:
        text = cap_path.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        if not body.strip():
            continue
        categoria = fm.get("categoria", "")
        obra_slug = fm.get("obra_slug", "")
        rank = get_priority_rank(categoria, obra_slug)
        chunks = split_into_subcenas(body)
        sub_total = len(chunks)

        # Identificador base: nome do arquivo sem .md (preserva sub-slug do Parva)
        base = cap_path.stem  # ex: 'L01-C01' ou 'on_dreams-L01-C01'
        obra_dir = cap_path.parent.parent  # obras/cat/obra/

        obra_idx = resolve_obra_idx(categoria, obra_slug, base)
        # slug humano-legível para o filename: usa sub_slug se houver,
        # senão obra_slug com prefixo numérico (ex: '01_etica_nicomaco') removido.
        slug_humano = re.sub(r"^\d+_", "", obra_slug)
        for sub in SUB_OBRA_IDX:
            if base.startswith(sub + "-"):
                slug_humano = sub
                break

        for i, chunk in enumerate(chunks, 1):
            sub_slug = f"{base}_cena{i:02d}"
            cena_path = obra_dir / "cenas" / f"{sub_slug}.md"
            prompt_path = obra_dir / "prompts" / f"{sub_slug}.md"
            audio_filename = build_audio_filename(
                obra_idx, fm.get("livro_num", 0), fm.get("capitulo_num", 0),
                i, slug_humano)
            cenas.append({
                "cena_id": f"{categoria}/{obra_slug}/{sub_slug}",
                "categoria": categoria,
                "obra_pt": fm.get("obra_pt", ""),
                "obra_en": fm.get("obra_en", ""),
                "obra_slug": obra_slug,
                "obra_idx": obra_idx,
                "fonte": fm.get("fonte", ""),
                "livro_num": fm.get("livro_num", 0),
                "livro_marker": fm.get("livro_marker", ""),
                "total_livros": fm.get("total_livros", 0),
                "capitulo_num": fm.get("capitulo_num", 0),
                "capitulo_marker": fm.get("capitulo_marker", ""),
                "total_capitulos_no_livro": fm.get("total_capitulos_no_livro", 0),
                "sub_cena_num": i,
                "sub_cena_total": sub_total,
                "chars": len(chunk),
                "priority_rank": rank,
                "capitulo_path": str(cap_path.relative_to(PROJECT_ROOT)),
                "cena_path": str(cena_path.relative_to(PROJECT_ROOT)),
                "prompt_path": str(prompt_path.relative_to(PROJECT_ROOT)),
                "audio_filename": audio_filename,
                "audio_title": audio_filename.removesuffix(".m4a"),
                "first_sentence": first_sentence(chunk),
                "last_sentence": last_sentence(chunk),
                "_chunk_text": chunk,  # privado — usado pelo runner; removido no JSON final
                "status": "pending",
                "done_at": None,
            })
    return cenas


def sort_cenas(cenas: list[dict]) -> list[dict]:
    """Ordena por priority_rank → livro → capítulo → sub-cena."""
    return sorted(cenas, key=lambda c: (
        c["priority_rank"], c["livro_num"], c["capitulo_num"], c["sub_cena_num"]))


def annotate_audio_position(cenas: list[dict]) -> None:
    """Adiciona audio_in_obra_idx / total_in_obra para o template 'audio X of Y'."""
    from collections import defaultdict
    by_obra: dict[tuple, list[dict]] = defaultdict(list)
    for c in cenas:
        by_obra[(c["categoria"], c["obra_slug"])].append(c)
    for key, lst in by_obra.items():
        for i, c in enumerate(lst, 1):
            c["audio_in_obra_idx"] = i
            c["audio_in_obra_total"] = len(lst)


def merge_with_existing(new: list[dict], existing: list[dict]) -> list[dict]:
    """Preserva status/done_at de cenas que já estavam no master anterior."""
    old = {c["cena_id"]: c for c in existing}
    for c in new:
        prev = old.get(c["cena_id"])
        if prev:
            c["status"] = prev.get("status", "pending")
            c["done_at"] = prev.get("done_at")
    return new


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Apenas mostra estatísticas; não grava o JSON.")
    parser.add_argument("--force", action="store_true",
                        help="Sobrescreve o master, preservando status das cenas existentes.")
    args = parser.parse_args()

    cenas = collect_capitulos()
    cenas = sort_cenas(cenas)
    annotate_audio_position(cenas)

    existing_status_count = {"pending": 0, "done": 0, "failed": 0}
    if MASTER_PATH.exists() and (args.force or not args.dry_run):
        try:
            existing = json.loads(MASTER_PATH.read_text(encoding="utf-8"))
            cenas = merge_with_existing(cenas, existing.get("cenas", []))
            for c in cenas:
                s = c.get("status", "pending")
                existing_status_count[s] = existing_status_count.get(s, 0) + 1
        except Exception as exc:  # noqa: BLE001
            print(f"AVISO: não foi possível ler master anterior: {exc}")

    # estatísticas
    total = len(cenas)
    longas = sum(1 for c in cenas if c["sub_cena_total"] > 1)
    from collections import Counter
    rank_counter: Counter[int] = Counter(c["priority_rank"] for c in cenas)
    print(f"=== Master cenas — {total} cenas planejadas ===")
    print(f"Capítulos divididos em múltiplas sub-cenas: {longas}")
    print(f"Estimativa @ 100/dia: {(total + 99) // 100} dias")
    print()
    print("Por priority_rank (top 10):")
    for rank, count in sorted(rank_counter.items())[:10]:
        # encontra obra desse rank
        for c in cenas:
            if c["priority_rank"] == rank:
                print(f"  rank {rank:2d}  {c['categoria']}/{c['obra_slug']:30s}  {count:4d} cenas")
                break
    if any(existing_status_count.values()):
        print()
        print("Status atual (merge com master existente):")
        for k, v in existing_status_count.items():
            print(f"  {k}: {v}")

    if args.dry_run:
        return 0

    # Remove _chunk_text antes de serializar (text fica nos arquivos cena .md)
    out_cenas = [{k: v for k, v in c.items() if not k.startswith("_")} for c in cenas]
    master = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": total,
        "max_chars_per_cena": MAX_CHARS_PER_CENA,
        "priority_order_source": "docs/priority_order.md + scripts/04_define_cenas_master.py",
        "cenas": out_cenas,
    }
    MASTER_PATH.parent.mkdir(parents=True, exist_ok=True)
    MASTER_PATH.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nMaster gravado: {MASTER_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
