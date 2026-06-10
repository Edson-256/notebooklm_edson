"""naming.py — nomes de arquivo que ORDENAM na sequência lógica de audição.

Prefixo `DD`+letra (mesmo tamanho p/ todos) → ordenação alfabética = ordem de ouvir:
  00a livro pórtico-geral · 00b livro léxico · 01a..01c cap01 (A→B→D) · … ·
  12c cap12 · 99a livro filtro-tese (síntese, por último).

A letra (a,b,c…) é a posição do formato no STACK do capítulo, ordenado pela
sequência do leque (pórtico→reconstrução→arena→filtro→meditatio→léxico).
Usado por 03_build_prompts.py e 05_frye_runner.py (fonte única do nome).
"""
from __future__ import annotations

LEQUE = ["portico", "reconstrucao", "arena", "filtro", "meditatio", "lexico"]

# formato camada-livro -> (grupo, letra, descritivo). Grupo "0"=início, "9"=fim.
BOOK = {
    "portico_geral": ("0", "a", "livro_portico-geral"),
    "lexico_geral":  ("0", "b", "livro_lexico-geral"),
    "filtro_tese":   ("9", "a", "livro_filtro-tese"),
}


def stem(cap, formato: str, formatos: list[str], width: int = 2) -> str:
    """Nome-base (sem extensão) já com o prefixo de ordenação."""
    w = max(2, width)
    if formato in BOOK:
        grp, letter, desc = BOOK[formato]
        dd = grp * w
        return f"{dd}{letter}_{desc}"
    dd = f"{int(cap):0{w}d}"
    ordered = sorted(formatos, key=lambda f: LEQUE.index(f))
    letter = chr(ord("a") + ordered.index(formato))
    return f"{dd}{letter}_cap{dd}_{formato}"
