#!/bin/bash
# Instalador de Cron Job para Shakespeare Audio Generator

set -e

PROJECT_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson"
SCRIPT_PATH="$PROJECT_DIR/scripts/daily_shakespeare_batch.py"
LOG_FILE="$PROJECT_DIR/logs/cron_shakespeare.log"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🎭 Shakespeare Audio Generator - Instalador de Cron Job  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar se o script existe
if [ ! -f "$SCRIPT_PATH" ]; then
    echo -e "${RED}❌ Erro: Script não encontrado em $SCRIPT_PATH${NC}"
    exit 1
fi

# Tornar script executável
chmod +x "$SCRIPT_PATH"
echo -e "${GREEN}✅ Script configurado como executável${NC}"

# Criar diretório de logs
mkdir -p "$PROJECT_DIR/logs"
echo -e "${GREEN}✅ Diretório de logs criado${NC}"

# Testar execução do script (dry-run)
echo ""
echo -e "${YELLOW}🧪 Testando script com dry-run...${NC}"
echo ""
python3 "$SCRIPT_PATH" --dry-run

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Erro ao executar script de teste${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✅ Script testado com sucesso!${NC}"
echo ""

# Configurar cron job
echo -e "${YELLOW}📅 Configurando cron job...${NC}"
echo ""
echo "O cron job será configurado para executar diariamente às 06:00"
echo ""
echo -e "${BLUE}Comando do cron job:${NC}"
CRON_CMD="0 6 * * * cd $PROJECT_DIR && /usr/bin/python3 $SCRIPT_PATH >> $LOG_FILE 2>&1"
echo "$CRON_CMD"
echo ""

read -p "Deseja instalar este cron job? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    # Backup do crontab atual
    crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true

    # Remover cron job existente (se houver)
    (crontab -l 2>/dev/null | grep -v "daily_shakespeare_batch.py" || true) | crontab -

    # Adicionar novo cron job
    (crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

    echo -e "${GREEN}✅ Cron job instalado com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}📋 Crontab atual:${NC}"
    crontab -l | grep shakespeare
    echo ""
    echo -e "${GREEN}🎉 Configuração concluída!${NC}"
    echo ""
    echo -e "${YELLOW}ℹ️  Informações importantes:${NC}"
    echo "   • O processamento começará amanhã às 06:00"
    echo "   • 20 cenas serão processadas por dia"
    echo "   • Logs salvos em: $LOG_FILE"
    echo "   • Progresso salvo em: $PROJECT_DIR/logs/shakespeare_progress.json"
    echo ""
    echo -e "${BLUE}📊 Comandos úteis:${NC}"
    echo "   • Ver logs: tail -f $LOG_FILE"
    echo "   • Ver progresso: cat $PROJECT_DIR/logs/shakespeare_progress.json | jq"
    echo "   • Teste manual: python3 $SCRIPT_PATH --dry-run"
    echo "   • Executar agora: python3 $SCRIPT_PATH"
    echo "   • Remover cron: crontab -e (deletar linha do shakespeare)"
    echo ""
else
    echo -e "${YELLOW}❌ Instalação cancelada${NC}"
    echo ""
    echo -e "${BLUE}Para instalar manualmente, adicione esta linha ao crontab:${NC}"
    echo "   crontab -e"
    echo ""
    echo "   $CRON_CMD"
    echo ""
fi
