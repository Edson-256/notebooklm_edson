#!/bin/bash
set -e

DIR="projetos/idiomas/alemao/A1"

for file in "$DIR"/licao_*.md; do
  echo "Formatando $file..."
  
  # Extrair apenas o texto markdown puro da resposta JSON e converter as quebras de linha
  jq -r '.value.answer' "$file" > "${file}.tmp"
  
  if [ -s "${file}.tmp" ] && [ "$(cat "${file}.tmp")" != "null" ]; then
    mv "${file}.tmp" "$file"
  else
    echo "Erro ao processar $file. O JSON pode estar malformado."
    rm -f "${file}.tmp"
  fi
done

echo "Formatação concluída com sucesso!"
