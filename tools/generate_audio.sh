#!/bin/bash
# Script para gerar audio overview de um notebook NotebookLM
# Uso: ./generate_audio.sh [NOTEBOOK_ID] [FORMAT] [LANGUAGE] [LENGTH]

set -e

# Configurações padrão
NOTEBOOK_ID="${1:?Erro: informe o NOTEBOOK_ID como primeiro argumento}"
FORMAT="${2:-deep_dive}"
LANGUAGE="${3:-pt-BR}"
LENGTH="${4:-default}"
PROFILE="${5:-default}"

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}🎙️  NotebookLM Audio Overview Generator${NC}"
echo -e "${BLUE}=================================================${NC}"
echo ""
echo -e "${GREEN}📋 Configuração:${NC}"
echo -e "  Notebook ID: ${YELLOW}${NOTEBOOK_ID}${NC}"
echo -e "  Formato: ${YELLOW}${FORMAT}${NC}"
echo -e "  Idioma: ${YELLOW}${LANGUAGE}${NC}"
echo -e "  Duração: ${YELLOW}${LENGTH}${NC}"
echo -e "  Perfil: ${YELLOW}${PROFILE}${NC}"
echo ""

# Verificar autenticação
echo -e "${BLUE}🔐 Verificando autenticação...${NC}"
if ! nlm login --check --profile "$PROFILE" 2>/dev/null; then
    echo -e "${RED}❌ Erro: Você precisa fazer login primeiro!${NC}"
    echo -e "${YELLOW}Execute: nlm login --profile $PROFILE${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Autenticado com sucesso!${NC}"
echo ""

# Gerar audio overview
echo -e "${BLUE}🎵 Gerando audio overview...${NC}"
echo -e "${YELLOW}Isso pode levar alguns minutos. Aguarde...${NC}"
echo ""

if nlm audio create "$NOTEBOOK_ID" \
    --format "$FORMAT" \
    --language "$LANGUAGE" \
    --length "$LENGTH" \
    --profile "$PROFILE" \
    --confirm; then

    echo ""
    echo -e "${GREEN}=================================================${NC}"
    echo -e "${GREEN}✅ Audio overview criado com sucesso!${NC}"
    echo -e "${GREEN}=================================================${NC}"
    echo ""
    echo -e "${BLUE}📥 Para baixar o áudio, execute:${NC}"
    echo -e "${YELLOW}nlm download $NOTEBOOK_ID --profile $PROFILE${NC}"
    echo ""

else
    echo ""
    echo -e "${RED}❌ Erro ao gerar audio overview${NC}"
    exit 1
fi
