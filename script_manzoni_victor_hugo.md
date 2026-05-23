Listed directory notebooklm_edson
Listed directory projetos
Listed directory scripts
Viewed README.md:1-278
Searched for "mazoni"
Listed directory mazoni
Listed directory I%20Promesi%20Sposi
Listed directory scripts
Viewed audio_runner.py:1-496
Listed directory victor_hugo
Listed directory notre-dame_de_paris
Listed directory scripts
Viewed audio_runner.py:1-493
Viewed cron_daily.sh:1-59

Para ambos os projetos, você possui um script unificado e automatizado chamado `scripts/audio_runner.py` que se encarrega de toda a inteligência: verificar o status das gerações no NotebookLM, baixar o áudio quando estiver pronto, salvá-lo com o nome padronizado no diretório `audios/` e atualizar o arquivo de controle local `metadata.json`.

Aqui estão os comandos exatos e como utilizá-los:

---

### 1. Projeto Manzoni (`I Promessi Sposi`)

Acesse a pasta do projeto:

```bash
cd "/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/mazoni/I Promesi Sposi"
```

* **Para baixar os áudios prontos e renomeá-los automaticamente:**
  ```bash
  python3 scripts/audio_runner.py --download
  ```

  *(O script baixará os áudios completos e os nomeará seguindo o padrão `promessi_XXX_nome_da_cena.m4a` na pasta `audios/`)*.
* **Para solicitar a geração do próximo lote de áudios (limite de 3 por dia):**
  ```bash
  python3 scripts/audio_runner.py --max 3
  ```
* **Para sincronizar áudios gerados manualmente no painel web (bootstrap):**
  ```bash
  python3 scripts/audio_runner.py --bootstrap
  ```

---

### 2. Projeto Victor Hugo (`Notre Dame de Paris`)

Acesse a pasta do projeto:

```bash
cd "/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/victor_hugo/notre-dame_de_paris"
```

* **Para baixar os áudios prontos e renomeá-los automaticamente:**
  ```bash
  python3 scripts/audio_runner.py --download
  ```

  *(O script baixará os áudios completos e os nomeará seguindo o padrão `notredame_XXX_nome_da_cena.m4a` na pasta `audios/`)*.
* **Para solicitar a geração do próximo lote de áudios:**
  ```bash
  python3 scripts/audio_runner.py --max 3
  ```
* **Para sincronizar áudios gerados manualmente no painel web (bootstrap):**
  ```bash
  python3 scripts/audio_runner.py --bootstrap
  ```

---

### 💡 Dicas importantes:

1. **Autenticação:** Se você receber um erro de autenticação, lembre-se de ativar/renovar sua credencial com o comando do CLI `nlm`:
   - Para o projeto em italiano (Manzoni): `nlm login --profile italiano`
   - Para o projeto em francês (Victor Hugo): `nlm login --profile frances`
2. **Visualizar o planejamento antes de rodar:** Você pode rodar com `--dry-run` para visualizar a fila de processamento sem disparar chamadas reais:
   ```bash
   python3 scripts/audio_runner.py --dry-run
   ```
