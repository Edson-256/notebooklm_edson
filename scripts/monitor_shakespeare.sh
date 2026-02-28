#!/bin/bash
# Monitor de progresso do gerador de áudios Shakespeare

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     📊 Monitor - Shakespeare Audio Generator              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar log do processo em background
LOG_FILE="/var/folders/d5/ph7_my291y74kmh2h5gxdbk80000gn/T/claude/-Users-edsonmichalkiewicz-dev-notebooklm-edson/tasks/b122844.output"

if [ -f "$LOG_FILE" ]; then
    echo "📄 Últimas 50 linhas do log:"
    echo "─────────────────────────────────────────────────────────────"
    tail -50 "$LOG_FILE"
    echo "─────────────────────────────────────────────────────────────"
else
    echo "⚠️  Log não encontrado"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar arquivos gerados
AUDIOS_DIR="/Users/edsonmichalkiewicz/dev/notebooklm_edson/w_shakespeare/*/audios"

echo "📁 Áudios gerados até agora:"
echo ""

COUNT=$(find $AUDIOS_DIR -name "*.mp3" 2>/dev/null | wc -l | tr -d ' ')

if [ "$COUNT" -gt 0 ]; then
    find $AUDIOS_DIR -name "*.mp3" -exec ls -lh {} \; 2>/dev/null | awk '{print "  📄", $9, "("$5")"}'
    echo ""
    echo "✅ Total: $COUNT áudio(s)"
else
    echo "  ⏳ Nenhum áudio baixado ainda..."
    echo "     (Aguarde alguns minutos para o primeiro áudio ser gerado)"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Verificar metadata
METADATA_FILES=$(find $AUDIOS_DIR -name "metadata.json" 2>/dev/null)

if [ -n "$METADATA_FILES" ]; then
    echo "📊 Metadata encontrado:"
    for meta in $METADATA_FILES; do
        if [ -f "$meta" ]; then
            obra=$(jq -r '.obra' "$meta" 2>/dev/null)
            total=$(jq -r '.total_cenas' "$meta" 2>/dev/null)
            echo "  📚 $obra: $total cena(s) processada(s)"
        fi
    done
fi

echo ""
echo "💡 Para ver log em tempo real:"
echo "   tail -f $LOG_FILE"
echo ""
echo "💡 Para parar o processo:"
echo "   pkill -f shakespeare_audio_generator"
