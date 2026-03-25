"""
Configuração central para o sistema de sync/archive de áudios.

Todos os scripts (sync_to_phone, mark_listened, cleanup_phone, archive_project)
importam deste módulo.
"""

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────
HOME = Path.home()
ICLOUD_AUDIO = HOME / "Library/Mobile Documents/com~apple~CloudDocs/audio"
REPO_EDSON = HOME / "dev/notebooklm_edson"
REPO_MICHALK = HOME / "dev/notebooklm_michalk"
GDRIVE_REMOTE = "gdrive"  # nome do remote no rclone config
GDRIVE_FOLDER_ID = "1CZQhrHaG7qRAaVy7I754K4LHs5ClKTgg"

# ─── Migração de pastas iCloud (nomes antigos → normalizados) ────────────────
ICLOUD_MIGRATION = {
    "Cálculo ": "calculo",
    "DeVita": "devita",
    "Docker": "docker",
    "Eric Voegelin": "eric_voegelin",
    "George Bernanos": "george_bernanos",
    "Louis Lavelle": "louis_lavelle",
    "Manzoni": "manzoni",
    "Tomas Aquino": "tomas_aquino",
    "VictorHugo": "victor_hugo",
    "g_flynn": "gone_girl",
    "l_wallace": "ben_hur",
    "w_shakespeare": "w_shakespeare",
}

# ─── Definição dos Projetos ──────────────────────────────────────────────────
# type: como o metadata está estruturado
#   "obra_multi"              — múltiplos metadata.json (Shakespeare: um por obra)
#   "obra_single"             — um metadata.json com audios[]
#   "chapter_index"           — chapter_index.json com chapters[]
#   "section_index_calculo"   — section_index.json com sections[].output_path relativo
#   "section_index_lehninger" — section_index.json com sections[].audio_file

PROJECTS = [
    {
        "id": "w_shakespeare",
        "label": "William Shakespeare",
        "repo": REPO_EDSON,
        "type": "obra_multi",
        "metadata_glob": "projetos/w_shakespeare/*/audios/metadata.json",
        "icloud_folder": "w_shakespeare",
    },
    {
        "id": "ben_hur",
        "label": "Ben-Hur (Lew Wallace)",
        "repo": REPO_EDSON,
        "type": "obra_single",
        "metadata_file": "projetos/ben-hur/audios/metadata.json",
        "icloud_folder": "ben_hur",
    },
    {
        "id": "devita",
        "label": "DeVita CME",
        "repo": REPO_MICHALK,
        "type": "chapter_index",
        "metadata_file": "projetos/devita_cme/chapter_index.json",
        "audio_dir": "projetos/devita_cme/audio",
        "icloud_folder": "devita",
    },
    {
        "id": "calculo",
        "label": "Cálculo (Munem Vol 1)",
        "repo": REPO_MICHALK,
        "type": "section_index_calculo",
        "metadata_file": "projetos/calculo/section_index.json",
        "audio_base": "projetos/calculo",
        "icloud_folder": "calculo",
    },
    {
        "id": "lehninger",
        "label": "Lehninger Bioquímica",
        "repo": REPO_MICHALK,
        "type": "section_index_lehninger",
        "metadata_file": "projetos/lehninger/section_index.json",
        "audio_dir": "projetos/lehninger/audio",
        "icloud_folder": "lehninger",
    },
]


def get_project(project_id: str) -> dict | None:
    """Retorna definição de projeto pelo ID."""
    for p in PROJECTS:
        if p["id"] == project_id:
            return p
    return None
