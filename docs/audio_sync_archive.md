# Sistema de Sync & Archive de Áudios

> Documento de referência — arquitetura, decisões técnicas e fluxo completo.
> Para uso rápido, veja [audio_sync_quickstart.md](audio_sync_quickstart.md).

## Problema

- 263+ áudios (~11 GB) espalhados entre dois repositórios (`notebooklm_edson`, `notebooklm_michalk`)
- Escuta feita 90% no iPhone, sem internet (carro, ônibus, fila, etc.)
- Pasta no iCloud mantinha arquivos offline, mas gerenciamento manual causava duplicatas e perda de controle

## Arquitetura

```
┌──────────────────────────────────────────────────────────────┐
│  MAC (dev) — geração de áudios                               │
│  notebooklm_edson/  e  notebooklm_michalk/                   │
│  Cada projeto tem metadata.json / chapter_index.json         │
├────────────────────┬─────────────────────────────────────────┤
│                    ↓  sync_to_phone.py                       │
│  iCLOUD DRIVE — fila de escuta (iPhone offline)              │
│  ~/Library/Mobile Documents/com~apple~CloudDocs/audio/       │
│  Subpastas normalizadas por projeto                          │
├────────────────────┬─────────────────────────────────────────┤
│                    ↓  archive_project.py (projeto concluído) │
│  GOOGLE DRIVE — arquivo frio permanente                      │
│  Folder ID: 1CZQhrHaG7qRAaVy7I754K4LHs5ClKTgg               │
│  Upload via rclone, verificação SHA256                       │
│  ~1.87 TB livres (conta pessoal)                             │
└──────────────────────────────────────────────────────────────┘
```

### Por que iCloud para escuta?

- Nativo no iPhone — Files app, sem app extra
- "Always Available Offline" funciona de forma confiável
- Sync automático Apple-to-Apple
- Sem dependência de terceiros

### Por que Google Drive para arquivo?

- 1.87 TB livres (130 GB usados de 2 TB)
- `rclone` suporta Google Drive (não suporta iCloud)
- Separa "ouvindo agora" de "já terminei" — evita confusão
- Acesso de qualquer lugar se precisar recuperar

## Projetos Rastreados

| ID | Label | Repo | Tipo Metadata | iCloud Folder |
|---|---|---|---|---|
| `w_shakespeare` | William Shakespeare | edson | `metadata.json` (múltiplos) | `w_shakespeare/` |
| `ben_hur` | Ben-Hur (Lew Wallace) | edson | `metadata.json` (único) | `ben_hur/` |
| `devita` | DeVita CME | michalk | `chapter_index.json` | `devita/` |
| `calculo` | Cálculo (Munem Vol 1) | michalk | `section_index.json` | `calculo/` |
| `lehninger` | Lehninger Bioquímica | michalk | `section_index.json` | `lehninger/` |

### Projetos Manuais (sem metadata automatizado)

Estes projetos têm áudios no iCloud mas não possuem metadata.json nos repositórios.
O script os preserva e lista no índice como "manual".

| iCloud Folder | Origem |
|---|---|
| `docker/` | NotebookLM Docker |
| `eric_voegelin/` | NotebookLM Eric Voegelin |
| `george_bernanos/` | NotebookLM George Bernanos |
| `louis_lavelle/` | NotebookLM Louis Lavelle |
| `manzoni/` | NotebookLM Manzoni |
| `tomas_aquino/` | NotebookLM Tomás de Aquino |
| `victor_hugo/` | NotebookLM Victor Hugo |
| `gone_girl/` | NotebookLM Gone Girl |

## Normalização de Pastas iCloud

Na primeira execução, o `sync_to_phone.py --migrate` reorganiza a pasta iCloud:

| Pasta Antiga | Pasta Nova | Motivo |
|---|---|---|
| `Cálculo ` (com espaço) | `calculo` | espaço trailing + acentos |
| `DeVita` | `devita` | padronizar lowercase |
| `Eric Voegelin` | `eric_voegelin` | espaços → underscore |
| `George Bernanos` | `george_bernanos` | espaços → underscore |
| `Louis Lavelle` | `louis_lavelle` | espaços → underscore |
| `Louis Lavelle-backup-*` | (conteúdo mesclado em `louis_lavelle`) | backup solto |
| `Manzoni` | `manzoni` | padronizar lowercase |
| `Tomas Aquino` | `tomas_aquino` | espaço → underscore |
| `VictorHugo` | `victor_hugo` | padronizar snake_case |
| `g_flynn` | `gone_girl` | nome mais claro |
| `l_wallace` | `ben_hur` | alinhar com projeto |

## Formatos de Metadata

### Tipo `obra` (Shakespeare, Ben-Hur)

```json
{
  "obra": "Hamlet",
  "audios": [
    {
      "arquivo": "ws_hamlet_01_contraste_teatro.mp3",
      "status": "downloaded",
      "output_path": "/abs/path/to/file.mp3",
      "listened": false,
      "synced_to_icloud": false
    }
  ]
}
```

### Tipo `chapter_index` (DeVita)

```json
{
  "chapters": [
    {
      "audio_file": "mk_devita_ch001_adolescents.m4a",
      "status": "downloaded",
      "listened": false,
      "synced_to_icloud": false
    }
  ]
}
```

### Tipo `section_index` (Cálculo, Lehninger)

```json
{
  "sections": [
    {
      "audio_file": "mk_leh_01.4_genetic_foundations.m4a",
      "audio_status": "downloaded",
      "output_path": "munem_vol1/audios/file.m4a",
      "listened": false,
      "synced_to_icloud": false
    }
  ]
}
```

## Scripts

| Script | Quando Usar | Descrição |
|---|---|---|
| `sync_to_phone.py` | Gerou áudio novo | Copia novos para iCloud, marca `synced_to_icloud`, gera `_index.txt` |
| `mark_listened.py` | Ouviu no celular | Marca `listened: true` no metadata por nome de arquivo |
| `cleanup_phone.py` | iCloud cheio | Remove do iCloud os marcados como `listened: true` |
| `archive_project.py` | Projeto concluído | Envia para GDrive via rclone, remove áudios do Mac |

### Campos adicionados pelo sistema

| Campo | Tipo | Adicionado por | Descrição |
|---|---|---|---|
| `listened` | bool | `mark_listened.py` | Indica se o áudio já foi ouvido |
| `synced_to_icloud` | bool | `sync_to_phone.py` | Indica se foi copiado para iCloud |
| `synced_at` | ISO datetime | `sync_to_phone.py` | Timestamp do sync |
| `archived` | bool | `archive_project.py` | Indica se foi enviado ao GDrive |
| `archived_at` | ISO datetime | `archive_project.py` | Timestamp do archive |
| `archive_path` | string | `archive_project.py` | Caminho no GDrive |

## Fluxo de Vida de um Áudio

```
[gerado] → downloaded
    ↓ sync_to_phone.py
[synced] → synced_to_icloud: true (cópia no iCloud)
    ↓ (usuário ouve no iPhone)
[ouvido] → listened: true (mark_listened.py)
    ↓ cleanup_phone.py
[limpo]  → removido do iCloud (cópia local permanece)
    ↓ archive_project.py (quando projeto concluído)
[arquivado] → archived: true, áudio removido do Mac
              metadata.json preservado localmente
```

## Setup Inicial (uma vez)

### 1. rclone (para archive no GDrive)

```bash
brew install rclone
rclone config
# Criar remote chamado "gdrive" com conta edson.michalkiewicz@gmail.com
# Tipo: Google Drive
# Scope: drive (full access)
```

### 2. Migração iCloud (primeira vez)

```bash
cd ~/dev/notebooklm_edson
python scripts/sync_to_phone.py --migrate
```

Isso renomeia as pastas existentes no iCloud para o padrão normalizado.

### 3. Sync inicial

```bash
python scripts/sync_to_phone.py
```

## Decisões Técnicas

1. **iCloud via filesystem, não API** — `shutil.copy2` para a pasta iCloud. O daemon do iCloud cuida do upload.
2. **Metadata como fonte de verdade** — O metadata.json/chapter_index.json de cada projeto é o registro canônico.
3. **Listened resetado do zero** — Todos os áudios iniciam com `listened: false` independente de já terem sido ouvidos antes.
4. **Sem dependência externa** — Apenas Python stdlib para sync (shutil, json, pathlib). rclone só para GDrive archive.
5. **Idempotente** — Rodar sync múltiplas vezes é seguro. Só copia o que falta.
