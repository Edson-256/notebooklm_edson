#!/bin/bash
# Demonstração: Como Claude pode usar o nlm CLI diretamente
# Este script mostra comandos que Claude pode executar automaticamente

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  🤖 Demonstração: Claude usando nlm CLI diretamente       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Função para executar comando e mostrar resultado
run_demo() {
    local description="$1"
    local command="$2"

    echo "┌────────────────────────────────────────────────────────────┐"
    echo "│ 📋 $description"
    echo "└────────────────────────────────────────────────────────────┘"
    echo "🔧 Comando: $command"
    echo ""

    if eval "$command"; then
        echo "✅ Sucesso!"
    else
        echo "❌ Erro (pode ser esperado se não autenticado)"
    fi
    echo ""
}

echo "🎯 O que Claude pode fazer com nlm CLI:"
echo ""

# 1. Verificar autenticação
run_demo "Verificar se está autenticado" "nlm login --check 2>&1 || true"

# 2. Listar notebooks (requer auth)
run_demo "Listar notebooks" "nlm notebook list 2>&1 || echo 'Requer autenticação'"

# 3. Ver informações de um notebook específico
run_demo "Obter informações do notebook Docker" \
    "nlm notebook get 85d38ec1-7659-4307-aedf-3bc773a4d4ba 2>&1 || echo 'Requer autenticação'"

# 4. Gerar audio overview
run_demo "Gerar audio overview do Docker" \
    "nlm audio create 85d38ec1-7659-4307-aedf-3bc773a4d4ba --format deep_dive --language pt-BR --confirm 2>&1 || echo 'Requer autenticação'"

echo "════════════════════════════════════════════════════════════════"
echo ""
echo "💡 Conclusão:"
echo ""
echo "   ✅ Claude PODE executar comandos nlm CLI diretamente"
echo "   ✅ Claude PODE criar scripts de automação"
echo "   ✅ Claude PODE configurar cron jobs"
echo "   ✅ Claude PODE processar múltiplos notebooks em batch"
echo ""
echo "   ⚠️  Requisito: Usuário precisa autenticar UMA VEZ"
echo "      Execute: nlm login"
echo ""
echo "════════════════════════════════════════════════════════════════"
