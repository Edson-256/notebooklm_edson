# Audio Sync — Guia Rápido

> Referência completa: [audio_sync_archive.md](audio_sync_archive.md)

## Comandos do Dia a Dia

```bash
# ─── Gerou áudios novos? Sincronize para o iPhone ───
python scripts/sync_to_phone.py

# ─── Ouviu um áudio? Marque como ouvido ───
python scripts/mark_listened.py ws_hamlet_01_contraste_teatro.mp3

# ─── Marcar vários de uma vez ───
python scripts/mark_listened.py ws_hamlet_01_contraste_teatro.mp3 ws_hamlet_02_irrupção_sobrenatural.mp3

# ─── Marcar todos de um projeto ───
python scripts/mark_listened.py --project ben_hur

# ─── iCloud cheio? Remova os já ouvidos ───
python scripts/cleanup_phone.py

# ─── Projeto concluído? Archive no Google Drive ───
python scripts/archive_project.py devita
```

## Ver Status

```bash
# ─── Resumo rápido de todos os projetos ───
python scripts/sync_to_phone.py --status

# ─── Só ver o que seria feito (sem copiar nada) ───
python scripts/sync_to_phone.py --dry-run
```

## Setup Inicial (uma vez)

```bash
# 1. Migrar pastas antigas do iCloud para formato padronizado
python scripts/sync_to_phone.py --migrate

# 2. Sync inicial (copia todos os áudios pendentes)
python scripts/sync_to_phone.py

# 3. (Opcional) Instalar rclone para archive no Google Drive
brew install rclone
rclone config  # criar remote "gdrive"
```

## Onde ficam os arquivos?

| Local | Caminho | Propósito |
|---|---|---|
| Áudios (Mac) | `projetos/*/audios/` | Cópia original de desenvolvimento |
| Áudios (iPhone) | iCloud Drive > audio > {projeto} | Escuta offline |
| Arquivo frio | Google Drive > NotebookLM_Archive | Backup permanente |
| Metadata | `projetos/*/audios/metadata.json` | Fonte de verdade |
| Índice iCloud | iCloud Drive > audio > `_index.txt` | Lista legível dos áudios no iPhone |

## Projetos Disponíveis

| ID | Nome | Áudios |
|---|---|---|
| `w_shakespeare` | William Shakespeare | ~37 cenas |
| `ben_hur` | Ben-Hur | 18 cenas |
| `devita` | DeVita CME | 108 capítulos |
| `calculo` | Cálculo Munem | 52 seções |
| `lehninger` | Lehninger Bioquímica | 78 seções |
