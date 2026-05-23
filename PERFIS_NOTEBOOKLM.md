# Isolamento de Perfis no NotebookLM (NLM_PROFILE)

Este documento registra a descoberta e o padrão arquitetural adotado para o isolamento de múltiplos perfis (profiles) da CLI do NotebookLM (`nlm`). 

Sempre que novos projetos forem iniciados ou runners de áudio forem criados, **utilize a variável de ambiente descrita aqui** para evitar problemas de concorrência e erros intermitentes de download.

---

## O Problema: Concorrência de Perfis Globais

A CLI `nlm` permite trabalhar com diferentes contas ou workspaces por meio de perfis (ex: `default`, `italiano`, `frances`). Tradicionalmente, para alternar entre perfis, executava-se o comando:

```bash
nlm login switch <nome-do-perfil>
```

No entanto, este comando altera o arquivo de configuração **global** da CLI (salvo em disco em `~/.config/nlm/` ou equivalente). 

Quando múltiplos scripts de áudio ou runners de diferentes projetos (como o italiano para *I Promessi Sposi* e o francês para *Notre-Dame de Paris*) rodam concorrentemente em segundo plano:
1. O Script A muda o perfil global para `frances`.
2. O Script B (quase simultaneamente) muda o perfil global para `italiano`.
3. O Script A tenta realizar um `nlm download audio` de um ID do notebook de Notre-Dame. Como o perfil global foi alterado para `italiano` pelo Script B, o download falha com a mensagem de erro genérica:
   `Error: Download failed for audio.`

---

## A Solução: A Variável de Ambiente `NLM_PROFILE`

A CLI do NotebookLM suporta o isolamento nativo de perfil via variável de ambiente. Em vez de usar comandos globais de alternância (`login switch`), podemos passar a variável `NLM_PROFILE` diretamente no escopo de ambiente do processo. 

Isso garante que **cada execução seja 100% isolada e segura para execução paralela** (thread-safe e race-free), sem que uma concorrência de scripts corrompa o perfil ativo um do outro.

### Como Implementar em Python

Abaixo está o padrão implementado e adotado em todos os runners do projeto (ex: `scripts/audio_runner.py`):

```python
import os
import subprocess

# Perfil específico deste projeto
PROFILE = "italiano"  # ou "frances", "default", etc.

def run_nlm(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """
    Invoca a CLI 'nlm' isolando o perfil via variável de ambiente.
    """
    # 1. Copia o ambiente atual do sistema
    env = os.environ.copy()
    
    # 2. Injeta a variável de perfil isolada para este subprocesso
    env["NLM_PROFILE"] = PROFILE
    
    # 3. Executa o comando nlm passando o ambiente modificado
    return subprocess.run(
        ["nlm", *args],
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout
    )
```

E para comandos individuais dentro dos runners, passamos também o `--profile` explícito quando suportado pela API da CLI:

```python
# Exemplo de comando que aceita --profile de forma explícita
r = run_nlm(["login", "--check", "--profile", PROFILE], timeout=30)
```

---

## Perfis Ativos Conhecidos no Repositório

Ao criar novos projetos, mapeie o perfil correspondente na variável `PROFILE` do runner:

* `default`: Usado para a maior parte dos projetos padrão.
* `italiano`: Vinculado ao projeto *Manzoni / I Promessi Sposi*.
* `frances`: Vinculado ao projeto *Victor Hugo / Notre-Dame de Paris*.

---

> [!IMPORTANT]
> **Nunca** utilize `nlm login switch` dentro de scripts automatizados ou cron jobs. Sempre utilize a variável de ambiente `NLM_PROFILE` injetada localmente no contexto de execução do subprocesso.
