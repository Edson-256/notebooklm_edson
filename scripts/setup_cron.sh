#!/bin/bash
# Script para configurar cron jobs para geração automática de audio overviews

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║     🕐 Configurador de Cron Jobs - NotebookLM Audio Overviews     ║
╚════════════════════════════════════════════════════════════════════╝

Este script ajuda a configurar agendamentos automáticos para gerar
audio overviews dos seus notebooks NotebookLM.

Exemplos de Cron Jobs:
───────────────────────────────────────────────────────────────────

1️⃣  Gerar audio do notebook Docker toda segunda-feira às 8h:
   0 8 * * 1 cd PROJECT_DIR && ./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba

2️⃣  Gerar batch de notebooks todo domingo às 22h:
   0 22 * * 0 cd PROJECT_DIR && python3 scripts/batch_audio_generator.py

3️⃣  Gerar audio diariamente às 6h da manhã:
   0 6 * * * cd PROJECT_DIR && ./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba

4️⃣  Gerar audio a cada 3 dias às 14h:
   0 14 */3 * * cd PROJECT_DIR && ./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba

Formato do Cron:
   ┌───────────── minuto (0 - 59)
   │ ┌───────────── hora (0 - 23)
   │ │ ┌───────────── dia do mês (1 - 31)
   │ │ │ ┌───────────── mês (1 - 12)
   │ │ │ │ ┌───────────── dia da semana (0 - 6) (0=Domingo)
   │ │ │ │ │
   * * * * * comando a executar

═══════════════════════════════════════════════════════════════════════

EOF

echo "Diretório do projeto: $PROJECT_DIR"
echo ""

# Função para adicionar cron job
add_cron_job() {
    local schedule="$1"
    local command="$2"
    local description="$3"

    echo "══════════════════════════════════════════════════════════"
    echo "Adicionar: $description"
    echo "Agendamento: $schedule"
    echo "Comando: $command"
    echo "══════════════════════════════════════════════════════════"
    echo ""
    read -p "Deseja adicionar este cron job? (s/N): " confirm

    if [[ "$confirm" =~ ^[Ss]$ ]]; then
        # Adicionar ao crontab
        (crontab -l 2>/dev/null; echo "$schedule cd $PROJECT_DIR && $command") | crontab -
        echo "✅ Cron job adicionado com sucesso!"
    else
        echo "❌ Cancelado."
    fi
    echo ""
}

# Menu interativo
echo "Escolha uma opção:"
echo ""
echo "1) Gerar audio toda segunda-feira às 8h (Notebook Docker)"
echo "2) Gerar batch de notebooks todo domingo às 22h"
echo "3) Gerar audio diariamente às 6h (Notebook Docker)"
echo "4) Configuração personalizada"
echo "5) Ver cron jobs atuais"
echo "6) Remover todos os cron jobs do NotebookLM"
echo "0) Sair"
echo ""
read -p "Opção: " option

case $option in
    1)
        add_cron_job \
            "0 8 * * 1" \
            "./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba" \
            "Audio do Docker toda segunda às 8h"
        ;;
    2)
        add_cron_job \
            "0 22 * * 0" \
            "python3 scripts/batch_audio_generator.py" \
            "Batch de notebooks todo domingo às 22h"
        ;;
    3)
        add_cron_job \
            "0 6 * * *" \
            "./scripts/generate_audio.sh 85d38ec1-7659-4307-aedf-3bc773a4d4ba" \
            "Audio do Docker diariamente às 6h"
        ;;
    4)
        echo "──────────────────────────────────────────"
        echo "Configuração Personalizada"
        echo "──────────────────────────────────────────"
        echo ""
        read -p "Minuto (0-59): " minute
        read -p "Hora (0-23): " hour
        read -p "Dia do mês (1-31, * para todos): " day
        read -p "Mês (1-12, * para todos): " month
        read -p "Dia da semana (0-6, * para todos): " weekday
        read -p "Notebook ID: " notebook_id
        read -p "Formato (deep_dive/brief/critique/debate): " format
        read -p "Idioma (pt-BR/en/es): " language

        schedule="$minute $hour $day $month $weekday"
        command="./scripts/generate_audio.sh $notebook_id $format $language"

        add_cron_job "$schedule" "$command" "Configuração personalizada"
        ;;
    5)
        echo "══════════════════════════════════════════════════════════"
        echo "Cron Jobs Atuais:"
        echo "══════════════════════════════════════════════════════════"
        crontab -l 2>/dev/null | grep -i "notebooklm\|generate_audio\|batch_audio" || echo "Nenhum cron job encontrado."
        echo ""
        ;;
    6)
        echo "⚠️  ATENÇÃO: Isso removerá TODOS os cron jobs relacionados ao NotebookLM!"
        read -p "Tem certeza? (s/N): " confirm
        if [[ "$confirm" =~ ^[Ss]$ ]]; then
            crontab -l 2>/dev/null | grep -v "generate_audio\|batch_audio" | crontab -
            echo "✅ Cron jobs removidos."
        else
            echo "❌ Cancelado."
        fi
        ;;
    0)
        echo "Até logo!"
        exit 0
        ;;
    *)
        echo "Opção inválida."
        exit 1
        ;;
esac

echo ""
echo "══════════════════════════════════════════════════════════"
echo "💡 Dicas:"
echo "══════════════════════════════════════════════════════════"
echo "• Para ver seus cron jobs: crontab -l"
echo "• Para editar manualmente: crontab -e"
echo "• Logs do cron: grep CRON /var/log/syslog (Linux) ou"
echo "                 log show --predicate 'process == \"cron\"' (macOS)"
echo "══════════════════════════════════════════════════════════"
