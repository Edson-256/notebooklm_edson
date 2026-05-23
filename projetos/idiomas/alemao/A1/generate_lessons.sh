#!/bin/bash
set -e

NOTEBOOK_ID="d713f15e-fc7f-43d0-9af7-84f11143c5a9"
DEST_DIR="projetos/idiomas/alemao/A1"

echo "Gerando Lição 1.1..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 1.1: Erradicação da Epêntese Vocálica'. O foco é eliminar a inserção involuntária da vogal /i/ ao pronunciar clusters consonantais no início ou fim de sílabas. O material deve ser estruturado em Markdown, direcionado para falantes de português brasileiro, incluindo explicação fonética baseada nas fontes, exemplos (Psychologie, Herbst, du fährst, Arzt) e um roteiro prático de exercícios de shadowing." > "$DEST_DIR/licao_1_1.md"

echo "Gerando Lição 1.2..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 1.2: Bloqueio da Coarticulação Nasal'. O foco é desaprender a nasalização automática do português brasileiro. Vogais posicionadas antes de consoantes nasais (/m/, /n/) devem permanecer estritamente orais. O material deve ser estruturado em Markdown, incluindo explicação, exemplos contrastivos e exercícios práticos." > "$DEST_DIR/licao_1_2.md"

echo "Gerando Lição 1.3..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 1.3: Consciência de Duração Vocálica'. O foco é dominar a distinção entre vogais longas e curtas como característica fonêmica independente. O material deve ser estruturado em Markdown, incluindo a explicação baseada nas fontes, pares mínimos, exemplos e exercícios práticos." > "$DEST_DIR/licao_1_3.md"

echo "Gerando Lição 2.1..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 2.1: Estrutura Rígida (SVO) e Apresentação'. O foco é formular introduções pessoais e internalizar a regra de posição fixa do verbo conjugado (V2) no Nominativo. O material deve ser estruturado em Markdown, contendo explicação, exemplos e exercícios práticos." > "$DEST_DIR/licao_2_1.md"

echo "Gerando Lição 2.2..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 2.2: A Tríade Cromática do Nominativo'. O foco é implementar a codificação por cores (Azul para Masculino, Vermelho para Feminino, Verde para Neutro) para acelerar a assimilação do gênero gramatical. O material deve ser estruturado em Markdown, contendo explicação e exercícios práticos." > "$DEST_DIR/licao_2_2.md"

echo "Gerando Lição 3.1..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 3.1: O Marcador de Contraste Masculino'. O foco é compreender que o Acusativo altera primariamente o gênero masculino (der -> den). O material deve ser estruturado em Markdown, contendo explicação e exercícios de fixação." > "$DEST_DIR/licao_3_1.md"

echo "Gerando Lição 3.2..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 3.2: Chunking de Verbos de Ação'. O foco é ensinar blocos indivisíveis atrelando verbos de alta frequência ao objeto no acusativo (ex: ich brauche den Kaffee). O material deve ser estruturado em Markdown, contendo explicação e exercícios práticos." > "$DEST_DIR/licao_3_2.md"

echo "Gerando Lição 3.3..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 3.3: Role-Play de Baixa Pressão com IA'. O foco é simular diálogos de sobrevivência (café, compras). O material deve ser estruturado em Markdown com prompts para a IA e roteiro de treino." > "$DEST_DIR/licao_3_3.md"

echo "Gerando Lição 4.1..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 4.1: A Supremacia das Preposições'. O foco é treinar a verificação prioritária de preposições para determinar a declinação. O material deve ser estruturado em Markdown com explicação e exercícios." > "$DEST_DIR/licao_4_1.md"

echo "Gerando Lição 4.2..."
nlm query notebook "$NOTEBOOK_ID" "Crie o material de estudo completo para a 'Lição 4.2: Andaime Metacognitivo (Scaffolding)'. O foco é o uso de prompts para forçar a autocorreção com IA. O material deve ser estruturado em Markdown, contendo os prompts e instruções de como usar." > "$DEST_DIR/licao_4_2.md"

echo "Geração concluída!"
