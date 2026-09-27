#!/bin/bash
# One-shot (2026-09-27, bd notebooklm_edson-n2yv): completa a Introduzione (cena 4)
# que ficou para trás por rate-limit da conta italiana (~3 áudios/dia).
#
# Roda o cron diário normal (baixa o que estiver pronto + cria o que faltar) e,
# para cada cena 001-004 que já esteja no dell, retroage a data do arquivo para
# antes da cena 005 — o feed do manzoni usa a data do arquivo como pubDate, e sem
# isso a cena apareceria como episódio mais novo, no fim da série.
#
# Quando o metadata mostrar 355 baixados, remove a própria linha do crontab.
set -u
DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson/projetos/literatura/mazoni/I Promesi Sposi"
export PATH="/Users/edsonmichalkiewicz/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
export HOME="/Users/edsonmichalkiewicz"

bash "$DIR/scripts/cron_daily.sh"

/usr/bin/ssh -o BatchMode=yes -o ConnectTimeout=15 dell-server '
  cd /srv/podcasts/manzoni || exit 0
  for n in 1 2 3 4; do
    f=$(ls promessi_00${n}_*.m4a 2>/dev/null) || continue
    touch -d "2026-05-16 12:0${n}:00 -0300" "$f"
  done'

done_count=$(/opt/homebrew/bin/python3 -c "
import json
d = json.load(open('$DIR/audios/metadata.json'))
print(sum(1 for a in d['audios'] if a.get('status') == 'downloaded'))")

if [ "$done_count" -ge 355 ]; then
  crontab -l | grep -v 'oneshot_completar_introduzione' | crontab -
fi
