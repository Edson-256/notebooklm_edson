# Skill: `nlm-audio-pipeline` — Pipeline de áudio formativo (NotebookLM)

> **Objetivo:** generalizar o que foi feito no projeto **Quo Vadis** numa skill reutilizável que
> pega qualquer obra → fragmenta em capítulos → identifica **1–5 cenas por capítulo** → gera um
> prompt deep-dive por cena → cria os áudios no NotebookLM (uma conta por projeto, projetos em
> **paralelo**) → respeita a cota diária de cada conta → **baixa no dia seguinte** via cron →
> arquiva no dell-server → notifica no Telegram.
>
> Documento de **design** (não implementação). Baseia-se na auditoria de **7 runners reais**
> (quo_vadis, ben-hur, cof_v2, aristoteles, promessi, notre-dame, shakespeare). O quo_vadis é a
> base estrutural; o **cof_v2 é o "best-of-breed"** de robustez. Objetivo: consolidar o **melhor
> estado da arte de hoje**, corrigindo as divergências que foram surgindo projeto a projeto.

---

## 0. Resumo executivo: o que copiar de onde

| Etapa | Melhor referência | Por quê |
|---|---|---|
| Fragmentação em capítulos | quo_vadis (`QV-capitulos/`) | nomenclatura sequencial + source-map |
| Identificação de cenas | `leitura_formativa/01_*` (a **reescrever**: 1–5 por capítulo) | prompt COF base |
| Prompt por cena | quo_vadis (`prompts_cenas/`) | template sequencial, metodologia só no ep. 1 |
| **Isolamento de perfil** | **cof_v2:471** | `NLM_PROFILE` env var, **sem `login switch`** |
| Rate-limit como estado | cof_v2 (`_RATE_LIMITED` → `deferred`) | não perde a cena, re-tenta no dia seguinte |
| `poll_status` 3 estados | cof_v2 (`_POLL_MISSING`/`_POLL_ERROR`) | distingue "perdido" de "processando" |
| Download (retry curto) | cof_v2 (`backoffs=[0,90,240]s`) | salvaguarda intra-download |
| Sanity-check no startup | cof_v2 (`sanity_check`) | aborta antes de gastar cota |
| Manifesto JSON (não regex) | cof_v2 (`_sources_map.json`) | determinístico, source_id resolvido |
| Bootstrap/harvest manual | promessi / aristoteles | importa áudios feitos na UI |
| Keep-alive de sessão | `scripts/nlm_keepalive.sh` | renova cookies a cada 8h (launchd) |
| Telegram | `scripts/tg_notify.py` | **estender** p/ listar nomes de arquivo |
| Sync/lifecycle/feed | `dell_server/podcast_system/` | Mac → dell → DROBO + feed do podcast |

**Conclusão central:** o quo_vadis_runner.py **não** serve de base multi-conta — seu `check_auth()`
(linha 237) chama `nlm login switch`, que grava estado global e quebraria a execução paralela. A
skill segue o **cof_v2**: isolar cada processo só por `NLM_PROFILE`, **nunca** por `login switch`.

---

## 1. Os 10 passos → componentes da skill

### Passo 1 — Fragmentar a obra em capítulos
- **Entrada:** `.epub`, `.txt`, `.docx`, `.md` ou pasta **já fragmentada** (ex.: saída do Docling/OCR).
- **Saída:** `<projeto>/<SIGLA>-capitulos/` com nomes sequenciais `01_cap-01_Titulo.md`
  (prefácio/epílogo recebem número que mantém a ordem lógica).
- **Padding dinâmico (Passo 10):** conta os capítulos *antes* de nomear. `≤99`→2 dígitos (`01`);
  `≥100`→3 dígitos (`001`); `≥1000`→4. Largura fixa para o projeto inteiro.
- **Capítulo longo → split (≤35 min):** se a duração estimada do áudio do capítulo passar de
  **35 min**, dividir em `N = teto(duração/35)` partes (geralmente 2–3): `01_cap-01_p1`, `_p2`...
  As cenas do capítulo se ligam ao sub-fragmento correto.
  - **A confirmar:** estimar duração por contagem de palavras (narração ≈ 130–150 wpm). [Q3]
- **Já fragmentado:** se a pasta existir, a skill só **renomeia** ao padrão e pula este passo.

### Passo 2 — Identificar 1–5 cenas **por capítulo** (leitura formativa)
- **Granularidade:** a identificação roda **capítulo a capítulo**, pedindo **1–5 cenas naquele
  capítulo** (≠ "5–20 por obra" do template atual — será **reescrito**). 100 capítulos ⇒ ≥100 cenas.
- **Saída:** `<projeto>/cenas/01_cap-01_cena-01_Nome-da-Cena.md`. **Conteúdo da cena no idioma
  original da obra** (ver §D-idiomas).
- **Critério:** maximizar a metodologia COF — alta tensão moral, decisão existencial, monólogo
  interno, choque de perspectiva, oportunidade de "experiência vicariante".
- **Revisão humana:** o usuário confere/edita as cenas antes de gerar os prompts (evita gastar
  cota com cenas ruins).
- **Manifesto canônico:** `_cenas_manifest.json` com numeração **global contínua** (não reinicia
  por capítulo): `seq_global, cap, cena_local, title, localization, source_ids, prompt_path,
  resumo, justificativa, language`.

### Passo 3 — Prompt deep-dive por cena (template sequencial)
- **Saída:** `<projeto>/prompts_cenas/prompt_01_cap-01_cena-01_Nome.md` (`prompt_` + nome da cena).
- **Estrutura do template (a alma da skill):**
  1. **Persona:** "Aja como um tutor sênior de humanidades, didático e conversacional, para um
     leigo." (= o "Tutor Sênior").
  2. **Âncora de série:** "Este é o episódio **N de M**." É o que cria a jornada contínua.
  3. **Abertura do áudio:** anunciar "**cena X, capítulo Y** de *<obra>*" + 1–2 frases recapitulando
     a cena anterior (só o essencial p/ situar).
  4. **Corpo:** a cena, **citando qual dos 4 pilares** está em foco — **sem redefini-los**.
  5. **Fecho:** 1–2 frases adiantando a próxima cena (gancho).
- **Metodologia só no episódio 1:** a explicação completa da leitura formativa (4 pilares,
  experiência vicariante etc.) aparece **apenas no primeiro áudio**. Nos demais, só se **cita** o
  pilar. Corrige o anti-padrão do **Ben-Hur**, que repetia tudo a cada áudio (~1/4 do tempo perdido).
- **Idioma:** instruções em **inglês**; **diretiva de output explícita** conforme §D + flag
  `--language <lang>` no runner.
- **Limite `MAX_FOCUS_CHARS = 10000`:** **evitar truncamento** sempre que possível. Se truncar, a
  skill **avisa o nome do arquivo truncado** (log + Telegram) para revisão manual.

### Passo 4 — Autenticação (mantido como está)
- O `nlm` **não faz login headless por senha** (OAuth + 2FA). Modelo adotado: **keepalive +
  alerta Telegram**.
  - `nlm login --check --profile <p>` renova sessão ociosa (cookies válidos até 2027; Google
    invalida sessão parada em ~24h). `nlm_keepalive.sh` roda a cada 8h via launchd.
  - Sessão morta de vez → só `nlm login -p <perfil>` (browser) resolve → keepalive avisa no Telegram.
- **Antes de cada lote:** `check_auth()` por perfil; se falhar, marca conta indisponível, **não
  adivinha senha**, e notifica.

### Passo 5 — Runner via `nlm` CLI
- **Base:** estrutura do quo_vadis (fire-and-forget, retry, metadata, session log) + robustez do
  cof_v2 (rate-limit→`deferred`, poll 3-estados, sanity-check, backoff de download).
- **Flags:** `--dry-run`, `--max-scenes N`, `--from/--to`, `--cap N`, `--download`, `--bootstrap`,
  `--status` (legível), `--regen-prompts`. **Perfil fixado no config do projeto** (guard, ver §L5).

### Passo 6 — Cota diária por conta + tabela canônica
**Tabela conta ↔ perfil ↔ cota ↔ status** (fonte: usuário, 2026-06-06):

| Conta Google | `NLM_PROFILE` | Tipo | Cota/dia | Output padrão | Status p/ novos projetos |
|---|---|---|---|---|---|
| edson.michalkiewicz@gmail.com | `default` | Pro | 20 | pt-BR | ❌ ocupado (COF-2/Aristóteles) |
| edson@michalkcare.com | `profissional` ⚠️ | Pro | 20 | pt-BR | ✅ **livre** (alvo) |
| dredsonlm@gmail.com | `italiano` | Free | 3 | italiano | ❌ ocupado (Promessi Sposi) |
| edson1800.de@gmail.com | `frances` | Free | 3 | francês | ❌ ocupado (Notre-Dame) |
| edsonmdphd@gmail.com | `espanhol` | Free | 3 | espanhol | ⚠️ reservado (**Don Quixote**, em início) |
| edson0720.fr@gmail.com | `alemão` | Free | 3 | alemão | ⚠️ reservado (DE futuro — Fausto?) |

> **⚠️ Armadilha 1 — cross-wiring:** o domínio do email NÃO bate com o perfil:
> `edson0720.`**`fr`**`→alemão`, `edson1800.`**`de`**`→frances`. Usar **a tabela**, nunca heurística.
>
> **⚠️ Armadilha 2 — rótulo pro a confirmar:** o usuário rotulou michalkcare="pessoal"/gmail=
> "profissional"; o CLAUDE.md diz o inverso (`default`=gmail; `profissional`=michalkcare).
> Funcional certo: **gmail/`default` ocupado, michalkcare livre**. Falta confirmar (read-only)
> que michalkcare = `profissional` antes do 1º disparo. [Q1]

- **Contador próprio** por `(perfil, data-local)` em `audios/_daily_quota.json`; ao bater o teto,
  cenas restantes viram `deferred` (não `failed`). **Margem:** parar 1 abaixo do limite (19/20).
- **Reset:** à **meia-noite local**; o fuso real do NLM é desconhecido → margem + calibração
  empírica nos logs (ver §I do chat). Não assumir fuso.

### Passo 7 — Download no **dia seguinte** (sem 90 min)
- **Padrão cof_v2:** um job diário (launchd, sobrevive ao sleep do Mac) faz **2 fases**:
  **(1)** `--download` dos áudios criados na rodada anterior (já "maduros", horas depois);
  **(2)** cria o lote novo do dia. O gap criação→download passa a ser ~1 dia (folga enorme).
- `download_audio` mantém `backoffs=[0,90,240]s` só como salvaguarda intra-download. Idempotente:
  o que não estiver pronto é pulado e pego na próxima rodada. **Nada manual.**

### Passo 8 — Armazenar com nome = nome da cena
- `<projeto>/audios/01_cap-01_cena-01_Nome.m4a` (nome idêntico ao da cena; **`.m4a`**, nunca `.mp3`).
- Filenames em **NFC** (macOS é NFD; mismatch quebra o match do download).

### Passo 9 — Telegram (StudioM4_bot), 2 momentos
- **Após criação:** lista os nomes criados. **Após download (dia seguinte):** lista os baixados.
- Formato pedido:
  ```
  <projeto> YYYY-MM-DD - HH:MM
   arquivos criados:
   - 01_cap-01_cena-01_Fulano.m4a
   - 01_cap-01_cena-02_Cicrano.m4a
   arquivos baixados: 02
  ```
- Credenciais `STUDIOM4_TELEGRAM_*` em `~/.secrets` (o `tg_notify.py` já faz fallback). Adicionar
  subcomando que recebe a **lista de nomes**.

### Passo 10 — Padding ≥100 capítulos
- Incorporado no Passo 1 (largura dinâmica calculada uma vez por projeto).

---

## 2. Orquestração & paralelismo (CORRIGIDO)

**Fato (correção do usuário):** um notebook vive em **uma conta**. Outra conta **não** roda prompts
nesse notebook sem que ele seja **compartilhado/replicado**. Logo:

- **Paralelismo real e limpo = projetos diferentes em contas diferentes, simultâneos** (o que
  COF/Aristóteles/Promessi/Notre-Dame já fazem). O `NLM_PROFILE` isola cada processo → o cron da
  profissional e o da pessoal rodam ao mesmo tempo sem se atropelar.
- **Dentro de um mesmo livro**, usar 2+ contas exige **compartilhar** (Opção B) ou **replicar**
  (Opção C) o notebook — ver §3-estratégia.
- **Regra de ouro de implementação:** `NLM_PROFILE` em **todo** subprocess (inclusive `download
  audio`, que **não aceita `--profile`**); **nunca** `nlm login switch` no runner.

---

## 3. Estratégia conta pessoal × profissional (decisão pendente [Q4])

A profissional (Pro, 20/dia) está **ociosa** (o usuário consome os áudios CME/programação dela, que
exigem foco; gera mais na pessoal, de leitura formativa). Como aproveitá-la:

| Opção | Como | Prós | Contras |
|---|---|---|---|
| **A. Um livro por conta** *(recomendado)* | profissional ganha **seu próprio** livro pt-BR | zero compartilhamento; divisão limpa; paralelo automático | precisa definir o livro-alvo |
| **B. Compartilhar** notebook pessoal→profissional | share nativo; cota conta p/ quem **gera** | 20/dia da profissional sobre conteúdo da pessoal; acelera 1 livro p/ 40/dia | **testar** se o `nlm` CLI mira notebook compartilhado; mais admin; metadata marca a conta geradora |
| **C. Replicar** fontes na profissional | re-upload num notebook novo | independência total | duplica fontes |

- **Não fundir contas.** Manter a divisão (você sabe onde estão os notebooks). A **skill é a camada
  de administração unificada** (1 config/metadata/Telegram/lifecycle por projeto, qualquer conta).

**Objetivo real (esclarecido 2026-06-06):** a profissional (pt-BR, ociosa) serve para **escoar os
prompts pendentes de COF-2 e Aristóteles** (pessoal, gargalo de 20/dia). Logo **A sai de cena**;
a escolha é **B vs C**.

**Achados do `nlm` CLI:**
- `nlm share invite --email <conta> <notebook_id>` → compartilhamento **scriptável** (favorece B).
- `nlm audio create NOTEBOOK_ID --profile <p>` aceita qualquer notebook → *mecanicamente* a
  profissional pode gerar num notebook compartilhado.
- Notebooks da pessoal confirmados: **COF 2** (`5508086a…`, 121 fontes), **Aristóteles** (`48eb1ca3…`).
- ⚠️ **Perfil `profissional` com sessão EXPIRADA** → exige `nlm login -p profissional` antes de tudo.

**VEREDITO (2026-06-06): Opção B BLOQUEADA.** `nlm share invite COF-2 → edson@michalkcare.com`
retornou `BLOCKED_BY_ADMIN_POLICY` (gRPC code 7). A política do Workspace **michalkcare.com** proíbe
aquela conta de colaborar num notebook de conta pessoal/externa. Batemos no muro **antes** de gerar
— a questão "de quem é a cota?" ficou sem resposta. Nada foi alterado (COF-2 segue owner-only).

**Caminhos restantes p/ os 20/dia ociosos da profissional:**
- **C — replicar** fontes do COF-2/Aristóteles num notebook próprio da profissional → +20/dia
  garantido; custo: re-upload 121+ fontes + novo mapa de source_ids + remapear prompts. **A skill
  coordena** (2 notebooks, roteamento de cenas por conta/dia, download por perfil).
- **Mudar política do Workspace** (Google Admin) → desbloqueia B, mas ainda exigiria testar a cota;
  risco de segurança — não recomendado só por isso.
- **A′ — conteúdo próprio** da profissional (CBHPM/Auditoria, Cirurgia Oncológica, NCCN,
  Dermatologia, Jotform...) → uso imediato e sem setup, mas não escoa o backlog do COF/Aristóteles.

---

## 4. Metadados & estado (você não precisa ler JSON)

`audios/metadata.json` é **bookkeeping interno**. Exposto ao usuário via comando **`--status`
legível** (ex.: "Cap 3: 4/5 cenas baixadas, 1 deferida"). Campos por cena: `arquivo, seq_global,
cap, cena_local, titulo, localizacao, artifact_id, notebook_profile, prompt_path, prompt_chars,
truncado(bool), source_ids, language, status, output_path, tamanho_bytes`. **5 estados:**
`created → downloaded`, `deferred` (rate-limit), `lost_in_studio` (sumiu do studio), `server_failed`.

---

## 5. Lifecycle / dell-server / feed do podcast

Ao iniciar um projeto, a skill:
1. cria pasta no **dell-server** com o **slug do projeto**;
2. baixa os `.m4a` lá (Mac → dell → DROBO, padrão `podcast_system`); nunca deleta o artifact do
   studio NLM (acesso via app em viagem);
3. Telegram informa a **URL do feed** a adicionar no app:
   `https://edson:SENHA@dell-server.tail3f4f14.ts.net/<slug>/feed.xml`. A skill **não embute a
   senha** — lembra que ela está no **SplashID**.

---

## 6. Decisões tomadas vs. pendências

**Tomadas (2026-06-06):** keepalive+Telegram (sem senha headless) · só `NLM_PROFILE` (sem switch) ·
rate-limit→`deferred` · download dia seguinte via launchd · output pt-BR p/ pessoal+profissional e
idioma-do-perfil p/ os demais (sobreponível) · cenas no idioma original · prompts em inglês ·
metodologia só no ep. 1 · 1–5 cenas por capítulo · split de capítulo >35 min · evitar truncamento +
avisar · guard anti-colisão de perfil · não fundir contas (skill = camada de admin).

**Pendências antes de construir:**
- **[Q1] ✅** michalkcare = perfil `profissional` (confirmado pelo usuário).
- **[Q2] ✅** Alvo = **COF-2 e Aristóteles** (escoar pendências da pessoal na profissional ociosa).
- **[Q3] ✅** Split de capítulo: alvo **15–30 min**, estendendo a **35 min** quando necessário.
- **[Q4] ⏳** Opção **B BLOQUEADA** por política do Workspace (ver §3). Restam: **C** (replicar),
  mudar política, **A′** (conteúdo próprio da profissional) ou deixar a profissional quieta.
  **Aguardando escolha do usuário.**
- **[Q5] ⏳** `profissional` logada ✅; falta usuário logar `espanhol` (Don Quixote) e `alemão`;
  depois entram no keepalive.

---

## 7. Backlog de robustez (do cof_v2) + sugestões aprovadas

- [ ] `_RATE_LIMITED` → `deferred`; `poll_status` 3 estados; `download` backoff `[0,90,240]`
- [ ] `sanity_check` no startup (numeração contínua, prompts existem, source_ids válidos)
- [ ] manifesto **JSON** (não regex); session log com contadores created/failed/deferred/lost
- [ ] `--bootstrap`/`--harvest`: importar áudios criados na UI (multi-projeto)
- [ ] keepalive estendido aos perfis do projeto; `.m4a` + NFC
- [ ] `--dry-run` obrigatório antes de lote real
- [ ] validação pós-download (rejeitar arquivo suspeito <1 MB / <2 min como `server_failed`)
- [ ] guard anti-colisão de perfil (recusa disparar fora do perfil do projeto sem `--force`)
- [ ] registrar cada obra como **épico no Beads**, 1 issue por fase

---

*Auditoria-base: quo_vadis_runner.py (757 l.), cof_v2/scripts/06_audio_runner.py,
scripts/{nlm_keepalive.sh, tg_notify.py}, leitura_formativa/. Design — implementação pendente das
respostas [Q1]–[Q5].*
