#!/usr/bin/env python3
"""
Cria o notebook 'Aristóteles (completo)' na conta default e faz upload das 33
obras (obras/{cat}/{obra}/clean/*.txt) como sources.

Nomenclatura das sources segue ordem canônica do Corpus Aristotelicum:
    {NN}. {TITULO_EN} (Aristotle, tr. {TRANSLATOR})

Output:
- _raw/notebook_aristoteles.json — id do notebook + mapeamento obra_slug → source_id

Uso:
  python scripts/06_create_notebook_and_upload.py            # cria + upload tudo
  python scripts/06_create_notebook_and_upload.py --dry-run  # só mostra plano
  python scripts/06_create_notebook_and_upload.py --upload-only --notebook-id ID
        # pula criação, faz upload em notebook existente
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK_META = PROJECT_ROOT / "_raw" / "notebook_aristoteles.json"

NOTEBOOK_TITLE = "Aristóteles (completo)"

# Ordem canônica do Corpus Aristotelicum + título inglês + tradutor.
# Tupla: (categoria, obra_slug, clean_filename, titulo_en, titulo_pt, translator)
SOURCES_ORDER: list[tuple[str, str, str, str, str, str]] = [
    # === Organon (lógica) ===
    ("01_organon", "01_categorias", "categories.txt",
     "Categories", "Categorias", "Edghill"),
    ("01_organon", "02_da_interpretacao", "on_interpretation.txt",
     "On Interpretation", "Da Interpretação", "Edghill"),
    ("01_organon", "03_analiticos_anteriores", "prior_analytics.txt",
     "Prior Analytics", "Analíticos Anteriores", "Jenkinson"),
    ("01_organon", "04_analiticos_posteriores", "posterior_analytics.txt",
     "Posterior Analytics", "Analíticos Posteriores", "Mure"),
    ("01_organon", "05_topicos", "topics.txt",
     "Topics", "Tópicos", "Pickard-Cambridge"),
    ("01_organon", "06_refutacoes_sofisticas", "on_sophistical_refutations.txt",
     "On Sophistical Refutations", "Refutações Sofísticas", "Pickard-Cambridge"),
    # === Filosofia natural ===
    ("02_fisica", "01_fisica", "physics.txt",
     "Physics", "Física", "Hardie & Gaye"),
    ("02_fisica", "02_sobre_o_ceu", "on_the_heavens.txt",
     "On the Heavens", "Sobre o Céu", "Stocks"),
    ("02_fisica", "03_geracao_corrupcao", "on_generation_and_corruption.txt",
     "On Generation and Corruption", "Sobre a Geração e a Corrupção", "Joachim"),
    ("02_fisica", "04_meteorologia", "meteorology.txt",
     "Meteorology", "Meteorologia", "Webster"),
    # === Psicologia + Parva Naturalia ===
    ("03_psicologia_biologia", "01_de_anima", "on_the_soul.txt",
     "On the Soul (De Anima)", "Sobre a Alma (De Anima)", "Smith"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_sense_and_the_sensible.txt",
     "On Sense and the Sensible", "Parva Naturalia — Sobre o Sentido e o Sensível", "Beare"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_memory_and_reminiscence.txt",
     "On Memory and Reminiscence", "Parva Naturalia — Sobre a Memória e a Reminiscência", "Beare"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_sleep_and_sleeplessness.txt",
     "On Sleep and Sleeplessness", "Parva Naturalia — Sobre o Sono e a Vigília", "Beare"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_dreams.txt",
     "On Dreams", "Parva Naturalia — Sobre os Sonhos", "Beare"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_prophesying_by_dreams.txt",
     "On Prophesying by Dreams", "Parva Naturalia — Sobre a Adivinhação pelos Sonhos", "Beare"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_longevity_and_shortness_of_life.txt",
     "On Longevity and Shortness of Life", "Parva Naturalia — Sobre a Longevidade e a Brevidade da Vida", "Ross"),
    ("03_psicologia_biologia", "02_parva_naturalia", "on_youth_and_old_age_on_life_and_death_on_breathing.txt",
     "On Youth and Old Age, On Life and Death, On Breathing",
     "Parva Naturalia — Juventude e Velhice, Vida e Morte, Respiração", "Ross"),
    # === Biologia ===
    ("03_psicologia_biologia", "03_historia_animais", "the_history_of_animals.txt",
     "The History of Animals", "História dos Animais", "Thompson"),
    ("03_psicologia_biologia", "04_partes_animais", "on_the_parts_of_animals.txt",
     "On the Parts of Animals", "Sobre as Partes dos Animais", "Ogle"),
    ("03_psicologia_biologia", "05_movimento_animais", "on_the_motion_of_animals.txt",
     "On the Motion of Animals", "Sobre o Movimento dos Animais", "Farquharson"),
    ("03_psicologia_biologia", "06_marcha_animais", "on_the_gait_of_animals.txt",
     "On the Gait of Animals", "Sobre a Marcha dos Animais", "Farquharson"),
    ("03_psicologia_biologia", "07_geracao_animais", "on_the_generation_of_animals.txt",
     "On the Generation of Animals", "Sobre a Geração dos Animais", "Peck (Loeb)"),
    # === Metafísica ===
    ("04_metafisica", "01_metafisica", "metaphysics.txt",
     "Metaphysics", "Metafísica", "Ross"),
    # === Ética ===
    ("05_etica", "01_etica_nicomaco", "nicomachean_ethics.txt",
     "Nicomachean Ethics", "Ética a Nicômaco", "Ross"),
    ("05_etica", "02_etica_eudemo", "eudemian_ethics.txt",
     "Eudemian Ethics", "Ética a Eudemo", "Solomon (Loeb)"),
    ("05_etica", "03_magna_moralia", "magna_moralia.txt",
     "Magna Moralia", "Magna Moralia (atribuída)", "Stock (Oxford)"),
    ("05_etica", "03_magna_moralia", "on_virtues_and_vices.txt",
     "On Virtues and Vices", "Sobre as Virtudes e os Vícios (atribuída)", "Rackham (Loeb)"),
    # === Política ===
    ("06_politica", "01_politica", "politics.txt",
     "Politics", "Política", "Jowett"),
    ("06_politica", "02_constituicao_atenienses", "the_athenian_constitution.txt",
     "The Athenian Constitution", "Constituição dos Atenienses", "Kenyon"),
    ("06_politica", "03_economicos", "economics.txt",
     "Economics (Oeconomica)", "Econômicos (atribuída)", "Forster (Oxford)"),
    # === Retórica & Poética ===
    ("07_retorica_poetica", "01_retorica", "rhetoric.txt",
     "Rhetoric", "Retórica", "Rhys Roberts"),
    ("07_retorica_poetica", "02_poetica", "poetics.txt",
     "Poetics", "Poética", "Butcher"),
]


def source_title(idx: int, titulo_en: str, translator: str) -> str:
    """Padrão: '01. Categories (Aristotle, tr. Edghill)'."""
    return f"{idx:02d}. {titulo_en} (Aristotle, tr. {translator})"


def run_nlm(args: list[str], timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(["nlm", *args], capture_output=True, text=True, timeout=timeout)


def create_notebook(title: str) -> str:
    """Cria notebook e devolve o ID. Lança em caso de erro."""
    print(f"Criando notebook '{title}'...")
    r = run_nlm(["notebook", "create", title], timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"create falhou: {r.stderr.strip()[:300]}")
    # O comando imprime algo como "Created notebook: <id>" ou JSON. Tentamos parse.
    out = (r.stdout + "\n" + r.stderr).strip()
    # tenta encontrar UUID
    import re
    m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", out)
    if not m:
        raise RuntimeError(f"não consegui extrair id do create: {out[:300]}")
    return m.group(0)


def upload_source(notebook_id: str, file_path: Path, title: str,
                  *, dry_run: bool) -> dict:
    """Faz upload de um arquivo como source, retorna metadados."""
    if dry_run:
        return {"status": "dry_run", "file": str(file_path.relative_to(PROJECT_ROOT)),
                "title": title, "bytes": file_path.stat().st_size}

    cmd = ["source", "add", notebook_id,
           "--file", str(file_path), "--title", title,
           "--wait", "--wait-timeout", "300"]
    r = run_nlm(cmd, timeout=360)
    if r.returncode != 0:
        return {"status": "error", "file": str(file_path.relative_to(PROJECT_ROOT)),
                "title": title, "error": r.stderr.strip()[:500] or r.stdout.strip()[:500]}
    # tenta extrair source_id da saída
    import re
    out = r.stdout + "\n" + r.stderr
    m = re.search(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", out)
    source_id = m.group(0) if m else None
    return {"status": "ok", "file": str(file_path.relative_to(PROJECT_ROOT)),
            "title": title, "source_id": source_id,
            "raw_output": out.strip()[-300:]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--upload-only", action="store_true",
                        help="Pula a criação, usa notebook-id existente.")
    parser.add_argument("--notebook-id", default=None)
    args = parser.parse_args()

    # Validação inicial: todos os arquivos clean existem?
    sources = []
    for idx, (cat, obra, fname, titulo_en, titulo_pt, tr) in enumerate(SOURCES_ORDER, 1):
        path = PROJECT_ROOT / "obras" / cat / obra / "clean" / fname
        if not path.exists():
            print(f"AVISO: arquivo não existe → {path.relative_to(PROJECT_ROOT)}")
            continue
        sources.append({
            "idx": idx, "categoria": cat, "obra_slug": obra,
            "fname": fname, "titulo_en": titulo_en, "titulo_pt": titulo_pt,
            "translator": tr, "path": path, "bytes": path.stat().st_size,
        })

    if len(sources) != len(SOURCES_ORDER):
        print(f"ERRO: {len(SOURCES_ORDER) - len(sources)} arquivos faltando.")
        return 2

    total_bytes = sum(s["bytes"] for s in sources)
    print(f"=== {len(sources)} sources prontas; total {total_bytes/1024/1024:.2f} MB ===")
    print(f"Maior: {max(s['bytes'] for s in sources)/1024:.0f} KB "
          f"({max(sources, key=lambda s: s['bytes'])['titulo_en']})")
    print()

    if args.dry_run:
        print("=== PLAN (dry-run) — nomenclatura das sources ===")
        for s in sources:
            title = source_title(s["idx"], s["titulo_en"], s["translator"])
            print(f"  {title}  [{s['bytes']/1024:.0f} KB]  ← {s['path'].relative_to(PROJECT_ROOT)}")
        return 0

    # Cria notebook (ou usa existente)
    if args.upload_only:
        if not args.notebook_id:
            print("ERRO: --upload-only exige --notebook-id")
            return 2
        notebook_id = args.notebook_id
        print(f"Usando notebook existente: {notebook_id}")
    else:
        notebook_id = create_notebook(NOTEBOOK_TITLE)
        print(f"Notebook criado: {notebook_id}")
        # salva já o ID para recuperação caso o upload falhe
        NOTEBOOK_META.parent.mkdir(parents=True, exist_ok=True)
        NOTEBOOK_META.write_text(json.dumps({
            "notebook_id": notebook_id, "title": NOTEBOOK_TITLE,
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "sources": []
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    # Upload em loop
    results = []
    ok = 0
    failed = 0
    for s in sources:
        title = source_title(s["idx"], s["titulo_en"], s["translator"])
        print(f"[{s['idx']:02d}/{len(sources)}] {title}  ({s['bytes']/1024:.0f} KB)")
        res = upload_source(notebook_id, s["path"], title, dry_run=False)
        res.update({
            "idx": s["idx"], "categoria": s["categoria"], "obra_slug": s["obra_slug"],
            "titulo_en": s["titulo_en"], "titulo_pt": s["titulo_pt"],
            "translator": s["translator"], "bytes": s["bytes"],
        })
        results.append(res)
        if res["status"] == "ok":
            ok += 1
            print(f"     → OK  source_id={res.get('source_id', '?')[:8]}")
        else:
            failed += 1
            print(f"     → FAIL  {res.get('error', '?')[:200]}")
        # salva intermediário a cada upload
        NOTEBOOK_META.write_text(json.dumps({
            "notebook_id": notebook_id, "title": NOTEBOOK_TITLE,
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ok": ok, "failed": failed, "sources": results,
        }, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    print(f"=== Upload concluído: ok={ok}  failed={failed} ===")
    print(f"Notebook ID: {notebook_id}")
    print(f"Manifest: {NOTEBOOK_META.relative_to(PROJECT_ROOT)}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
