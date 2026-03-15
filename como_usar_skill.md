Sim, funciona para ambas as contas. As mudanças feitas no skill:

O que mudou
Antes: PROFILE = "profissional" hardcoded em todo lugar.

Agora: O profile é dinâmico em 3 camadas:


1. chapter_index.json  →  "profile": "profissional"  (valor padrão do projeto)
2. --profile default   →  CLI sobrescreve o JSON      (uso pontual)
3. Fallback            →  "profissional"              (se não definido)
Como usar

# Projeto na conta profissional (edson@michalkcare.com)
/notebooklm-audio-project fisiologia d23c673d-... --profile profissional

# Projeto na conta pessoal (edson.michalkiewicz@gmail.com)
/notebooklm-audio-project shakespeare 62400b1d-... --profile default
O profile fica salvo no chapter_index.json do projeto, então nos comandos do dia a dia não precisa repetir:


# O profile já está no JSON — sem precisar passar toda vez
python3 scripts/next_batch.py --go

# Mas se quiser sobrescrever pontualmente:
python3 scripts/next_batch.py --go --profile default
A mensagem de auth expirada também mostra o profile correto:


ERRO: Autenticação do NotebookLM expirada!

O token do profile 'default' expirou.

Execute: nlm login --profile default