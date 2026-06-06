#!/usr/bin/env python3
"""
Baixa o corpus aristotelicum em inglês a partir do Internet Classics Archive (MIT),
Wikisource e Archive.org para obras complementares.

Para cada obra do MIT usamos a versão text-only consolidada (.mb.txt) — todos os
"Books" de uma obra em um único arquivo, sem HTML/navegação.

Cada obra é salva em:
  obras/{categoria}/{obra}/_raw/{slug}.txt        (texto consolidado)
  obras/{categoria}/{obra}/_raw/{slug}.source.json (metadados: url, fonte, tradutor)

Uso:
  python scripts/01_download_corpus.py            # baixa tudo (skip cached)
  python scripts/01_download_corpus.py --only fisica   # filtra por categoria
  python scripts/01_download_corpus.py --force    # re-baixa mesmo se já existir
  python scripts/01_download_corpus.py --dry-run  # apenas lista o que faria
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Algumas requests com UA customizado caem em cache do Google (provavelmente filtro
# de bots no servidor MIT). Mozilla padrão evita esse fallback indesejado.
USER_AGENT = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/124.0.0.0 Safari/537.36")

# Corpus aristotelicum mapeado para fontes públicas.
# Para MIT, usamos a versão text-only consolidada (.mb.txt): todos os "Books" da obra
# em um único arquivo. URLs derivadas do slug do arquivo HTML do classics.mit.edu.
# Cada entrada: (slug_obra, titulo_pt, titulo_en, url, fonte)
CORPUS = {
    "01_organon": [
        ("01_categorias", "Categorias", "Categories",
         "https://classics.mit.edu/Aristotle/categories.mb.txt", "MIT/Oxford-Edghill"),
        ("02_da_interpretacao", "Da Interpretação", "On Interpretation",
         "https://classics.mit.edu/Aristotle/interpretation.mb.txt", "MIT/Oxford-Edghill"),
        ("03_analiticos_anteriores", "Analíticos Anteriores", "Prior Analytics",
         "https://classics.mit.edu/Aristotle/prior.mb.txt", "MIT/Oxford-Jenkinson"),
        ("04_analiticos_posteriores", "Analíticos Posteriores", "Posterior Analytics",
         "https://classics.mit.edu/Aristotle/posterior.mb.txt", "MIT/Oxford-Mure"),
        ("05_topicos", "Tópicos", "Topics",
         "https://classics.mit.edu/Aristotle/topics.mb.txt", "MIT/Oxford-Pickard-Cambridge"),
        ("06_refutacoes_sofisticas", "Refutações Sofísticas", "On Sophistical Refutations",
         "https://classics.mit.edu/Aristotle/sophist_refut.mb.txt", "MIT/Oxford-Pickard-Cambridge"),
    ],
    "02_fisica": [
        ("01_fisica", "Física", "Physics",
         "https://classics.mit.edu/Aristotle/physics.mb.txt", "MIT/Oxford-Hardie-Gaye"),
        ("02_sobre_o_ceu", "Sobre o Céu", "On the Heavens",
         "https://classics.mit.edu/Aristotle/heavens.mb.txt", "MIT/Oxford-Stocks"),
        ("03_geracao_corrupcao", "Sobre a Geração e a Corrupção", "On Generation and Corruption",
         "https://classics.mit.edu/Aristotle/gener_corr.mb.txt", "MIT/Oxford-Joachim"),
        ("04_meteorologia", "Meteorologia", "Meteorology",
         "https://classics.mit.edu/Aristotle/meteorology.mb.txt", "MIT/Oxford-Webster"),
    ],
    "03_psicologia_biologia": [
        ("01_de_anima", "Sobre a Alma (De Anima)", "On the Soul",
         "https://classics.mit.edu/Aristotle/soul.mb.txt", "MIT/Oxford-Smith"),
        # Parva Naturalia: coleção de 7 tratados curtos. Baixados como múltiplos arquivos.
        ("02_parva_naturalia", "Parva Naturalia — Sobre o Sentido e o Sensível", "On Sense and the Sensible",
         "https://classics.mit.edu/Aristotle/sense.mb.txt", "MIT/Oxford-Beare"),
        ("02_parva_naturalia", "Parva Naturalia — Sobre a Memória e a Reminiscência", "On Memory and Reminiscence",
         "https://classics.mit.edu/Aristotle/memory.mb.txt", "MIT/Oxford-Beare"),
        ("02_parva_naturalia", "Parva Naturalia — Sobre o Sono e a Vigília", "On Sleep and Sleeplessness",
         "https://classics.mit.edu/Aristotle/sleep.mb.txt", "MIT/Oxford-Beare"),
        ("02_parva_naturalia", "Parva Naturalia — Sobre os Sonhos", "On Dreams",
         "https://classics.mit.edu/Aristotle/dreams.mb.txt", "MIT/Oxford-Beare"),
        ("02_parva_naturalia", "Parva Naturalia — Sobre a Adivinhação pelos Sonhos", "On Prophesying by Dreams",
         "https://classics.mit.edu/Aristotle/prophesying.mb.txt", "MIT/Oxford-Beare"),
        ("02_parva_naturalia", "Parva Naturalia — Sobre a Longevidade e a Brevidade da Vida", "On Longevity and Shortness of Life",
         "https://classics.mit.edu/Aristotle/longev_short.mb.txt", "MIT/Oxford-Ross"),
        ("02_parva_naturalia", "Parva Naturalia — Juventude e Velhice, Vida e Morte, Respiração", "On Youth and Old Age, On Life and Death, On Breathing",
         "https://classics.mit.edu/Aristotle/youth_old.mb.txt", "MIT/Oxford-Ross"),
        ("03_historia_animais", "História dos Animais", "The History of Animals",
         "https://classics.mit.edu/Aristotle/history_anim.mb.txt", "MIT/Oxford-Thompson"),
        ("04_partes_animais", "Sobre as Partes dos Animais", "On the Parts of Animals",
         "https://classics.mit.edu/Aristotle/parts_animals.mb.txt", "MIT/Oxford-Ogle"),
        ("05_movimento_animais", "Sobre o Movimento dos Animais", "On the Motion of Animals",
         "https://classics.mit.edu/Aristotle/motion_animals.mb.txt", "MIT/Oxford-Farquharson"),
        ("06_marcha_animais", "Sobre a Marcha dos Animais", "On the Gait of Animals",
         "https://classics.mit.edu/Aristotle/gait_anim.mb.txt", "MIT/Oxford-Farquharson"),
        # Geração dos Animais não está no MIT — Archive.org (tradução A. L. Peck, Loeb)
        # NB: worksofaristotle05arisuoft é PARTS of Animals (vol V Oxford), não Generation!
        # Usar generationofanim00arisuoft (Peck) que é dedicado à obra.
        ("07_geracao_animais", "Sobre a Geração dos Animais", "On the Generation of Animals",
         "https://archive.org/download/generationofanim00arisuoft/generationofanim00arisuoft_djvu.txt",
         "Archive.org/Loeb-Peck"),
    ],
    "04_metafisica": [
        ("01_metafisica", "Metafísica", "Metaphysics",
         "https://classics.mit.edu/Aristotle/metaphysics.mb.txt", "MIT/Oxford-Ross"),
    ],
    "05_etica": [
        ("01_etica_nicomaco", "Ética a Nicômaco", "Nicomachean Ethics",
         "https://classics.mit.edu/Aristotle/nicomachaen.mb.txt", "MIT/Oxford-Ross"),
        # Eudemian Ethics, Magna Moralia: não estão no MIT. Archive.org volumes Oxford.
        # Eudemian Ethics está no vol. da Athenian Const + Virtues (tradução Solomon, Oxford)
        ("02_etica_eudemo", "Ética a Eudemo", "Eudemian Ethics",
         "https://archive.org/download/athenianconstitu00arisuoft/athenianconstitu00arisuoft_djvu.txt",
         "Archive.org/Oxford-Solomon"),
        ("03_magna_moralia", "Magna Moralia (Grande Ética, atribuída)", "Magna Moralia",
         "https://archive.org/download/magnamoralia00arisuoft/magnamoralia00arisuoft_djvu.txt",
         "Archive.org/Stock"),
        # Virtudes e Vícios (atribuído): Loeb LCL 285 (Athenian Const + Eudemian + Virtues
        # & Vices) tem todas no mesmo volume. Já baixado em 02_etica_eudemo; aqui reusamos.
        ("03_magna_moralia", "Sobre as Virtudes e os Vícios (atribuído)", "On Virtues and Vices",
         "https://archive.org/download/athenianconstitu00arisuoft/athenianconstitu00arisuoft_djvu.txt",
         "Archive.org/Loeb-Rackham"),
    ],
    "06_politica": [
        ("01_politica", "Política", "Politics",
         "https://classics.mit.edu/Aristotle/politics.mb.txt", "MIT/Oxford-Jowett"),
        ("02_constituicao_atenienses", "Constituição dos Atenienses", "The Athenian Constitution",
         "https://classics.mit.edu/Aristotle/athenian_const.mb.txt", "MIT/Oxford-Kenyon"),
        ("03_economicos", "Econômicos (atribuído)", "Economics",
         "https://archive.org/download/oeconomica01arisuoft/oeconomica01arisuoft_djvu.txt",
         "Archive.org/Oxford-Forster"),
    ],
    "07_retorica_poetica": [
        ("01_retorica", "Retórica", "Rhetoric",
         "https://classics.mit.edu/Aristotle/rhetoric.mb.txt", "MIT/Oxford-Roberts"),
        ("02_poetica", "Poética", "Poetics",
         "https://classics.mit.edu/Aristotle/poetics.mb.txt", "MIT/Oxford-Butcher"),
    ],
}


def fetch(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def fetch_with_fallback(url: str, timeout: int = 120) -> tuple[bytes, str]:
    """Para URLs do MIT em .mb.txt, tenta também .1b.txt (obras de livro único).
    Para Archive.org /stream/.../djvu.txt, fallback para /download/.../djvu.txt."""
    candidates = [url]
    if url.endswith(".mb.txt"):
        candidates.append(url.replace(".mb.txt", ".1b.txt"))
    if url.endswith(".mb.txt"):
        candidates.append(url.replace(".mb.txt", ".html"))  # último recurso
    if "archive.org/stream/" in url and url.endswith("_djvu.txt"):
        candidates.append(url.replace("/stream/", "/download/"))
    last_err: Exception | None = None
    for u in candidates:
        try:
            return fetch(u, timeout=timeout), u
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            continue
    raise last_err if last_err else RuntimeError("no candidates")


_GOOGLE_CACHE_MARK = "Google"
_PRE_RE = re.compile(r"<pre[^>]*>(.*?)</pre>", re.IGNORECASE | re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")
_HTML_ENTITIES = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"',
                  "&#39;": "'", "&nbsp;": " "}


def unwrap_google_cache(raw: str) -> str | None:
    """Se a resposta é um HTML do Google cache embrulhando um text-only do MIT,
    retorna apenas o texto real (dentro do <pre>...</pre>). Caso contrário, None."""
    head = raw[:2000]
    if "Google" not in head or "<pre" not in raw.lower():
        return None
    m = _PRE_RE.search(raw)
    if not m:
        return None
    inner = m.group(1)
    inner = _TAG_RE.sub("", inner)
    for ent, ch in _HTML_ENTITIES.items():
        inner = inner.replace(ent, ch)
    return inner.strip() + "\n"


def normalize_text(raw: str) -> str:
    """Normaliza encoding e quebras de linha; preserva parágrafos."""
    # remove BOM e normaliza line endings
    raw = raw.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    # colapsa 3+ linhas em branco para 2
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip() + "\n"


def slugify_filename(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[áàâãä]", "a", text)
    text = re.sub(r"[éèêë]", "e", text)
    text = re.sub(r"[íìîï]", "i", text)
    text = re.sub(r"[óòôõö]", "o", text)
    text = re.sub(r"[úùûü]", "u", text)
    text = re.sub(r"[ç]", "c", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def download_one(categoria: str, obra: str, titulo_pt: str, titulo_en: str,
                 url: str, fonte: str, *, dry_run: bool, force: bool) -> dict:
    obra_dir = PROJECT_ROOT / "obras" / categoria / obra / "_raw"
    obra_dir.mkdir(parents=True, exist_ok=True)

    slug = slugify_filename(titulo_en)
    txt_path = obra_dir / f"{slug}.txt"
    meta_path = obra_dir / f"{slug}.source.json"

    result = {
        "categoria": categoria,
        "obra": obra,
        "titulo_pt": titulo_pt,
        "titulo_en": titulo_en,
        "url": url,
        "fonte": fonte,
        "txt_path": str(txt_path.relative_to(PROJECT_ROOT)),
        "status": "skipped",
        "bytes_txt": 0,
        "error": None,
    }

    if dry_run:
        result["status"] = "dry_run"
        return result

    if not force and txt_path.exists() and txt_path.stat().st_size > 5000:
        result["status"] = "cached"
        result["bytes_txt"] = txt_path.stat().st_size
        return result

    try:
        raw, effective_url = fetch_with_fallback(url)
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = raw.decode("latin-1", errors="replace")

        # Sanity check: rejeita resposta vazia
        if len(text) < 5000:
            raise ValueError(f"resposta suspeita: apenas {len(text)} bytes")

        # Caso 1: MIT respondeu via Google cache (HTML embrulhando o text-only original)
        unwrapped = unwrap_google_cache(text)
        if unwrapped:
            text = unwrapped
            suffix_note = " [google-cache]"
            is_html = False
        else:
            is_html = "<html" in text[:2000].lower() or "<!DOCTYPE" in text[:200]
            suffix_note = " [HTML — pós-processar]" if is_html else ""

        text = normalize_text(text)
        txt_path.write_text(text, encoding="utf-8")
        result["bytes_txt"] = txt_path.stat().st_size

        meta = {
            "titulo_pt": titulo_pt,
            "titulo_en": titulo_en,
            "url": url,
            "fonte": fonte,
            "is_html_raw": is_html,
            "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        result["status"] = "ok" + suffix_note
    except Exception as exc:  # noqa: BLE001
        result["status"] = "error"
        result["error"] = f"{type(exc).__name__}: {exc}"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", default=None,
                        help="Categoria a baixar (ex: organon, fisica, etica). Substring match.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Apenas lista o que seria baixado.")
    parser.add_argument("--force", action="store_true",
                        help="Re-baixa mesmo se o arquivo já existir.")
    parser.add_argument("--sleep", type=float, default=1.5,
                        help="Pausa em segundos entre requests (default 1.5s).")
    args = parser.parse_args()

    all_results: list[dict] = []
    total = sum(len(items) for items in CORPUS.values())
    counter = 0

    for categoria, items in CORPUS.items():
        if args.only and args.only.lower() not in categoria.lower():
            continue
        print(f"\n=== {categoria} ({len(items)} obras) ===")
        for obra, titulo_pt, titulo_en, url, fonte in items:
            counter += 1
            print(f"[{counter:02d}/{total}] {obra} ← {fonte}: {titulo_en}")
            res = download_one(categoria, obra, titulo_pt, titulo_en, url, fonte,
                               dry_run=args.dry_run, force=args.force)
            print(f"        → {res['status']} ({res['bytes_txt']/1024:.1f} KB)")
            if res["error"]:
                print(f"        ! {res['error']}")
            all_results.append(res)
            if not args.dry_run and res["status"].startswith("ok"):
                time.sleep(args.sleep)

    # Manifesto consolidado
    manifest_path = PROJECT_ROOT / "_raw" / "download_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total": len(all_results),
        "ok": sum(1 for r in all_results if r["status"].startswith("ok")),
        "cached": sum(1 for r in all_results if r["status"] == "cached"),
        "errors": sum(1 for r in all_results if r["status"] == "error"),
        "results": all_results,
    }
    manifest_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nManifesto: {manifest_path.relative_to(PROJECT_ROOT)}")
    print(f"OK={summary['ok']}  Cached={summary['cached']}  Errors={summary['errors']}  Total={summary['total']}")

    return 0 if summary["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
