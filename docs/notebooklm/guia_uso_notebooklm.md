# Guia de Uso do NotebookLM no Claude (MCP)

Este guia explica como integrar seus notebooks do Google NotebookLM ao Claude usando o servidor MCP que acabamos de configurar.

## ⚠️ Limitação Importante
A versão atual do servidor (`v0.1.15`) não permite listar seus notebooks automaticamente. Você precisará **fornecer o ID do notebook** manualmente.

---

## 1. Como Encontrar o ID do seu Notebook

1.  Acesse [NotebookLM](https://notebooklm.google.com/).
2.  Abra o notebook que você deseja utilizar.
3.  Olhe para a barra de endereço do navegador (URL).
4.  O **ID** é o código final após `notebook/`.

**Exemplo:**
*   URL: `https://notebooklm.google.com/notebook/1a2b3c-4d5e6f-7g8h9i`
*   **ID**: `1a2b3c-4d5e6f-7g8h9i`

---

## 2. Como Usar no Claude

### Definir um Notebook Padrão
Para focar em um projeto específico:
> "Defina o notebook padrão para `[SEU_ID]`."

### Trabalhar com Múltiplos Notebooks
Se você usa vários projetos (ex: Oncologia, Finanças, Estudos), forneça os IDs e dê apelidos:
> "Vou usar dois notebooks:
> 1. Oncologia: ID `abc-123`
> 2. Finanças: ID `xyz-789`"

Depois, você pode referenciar pelo nome:
> "Pergunte ao notebook de Finanças sobre o relatório anual."
> "Agora mude para o notebook de Oncologia."

### Navegação (Opcional)
Se precisar abrir o notebook no navegador controlado pelo MCP:
> "Navegue para o notebook `[SEU_ID]`."

---

## 3. Comandos Disponíveis

O servidor MCP oferece as seguintes ferramentas que o Claude pode usar:

*   `navigate_to_notebook`: Abre um notebook específico.
*   `chat_with_notebook`: Envia uma mensagem e recebe a resposta do NotebookLM.
*   `get_chat_response`: Obtém a última resposta (útil para respostas longas).
*   `set_default_notebook`: Define qual notebook usar se nenhum for especificado.
*   `get_default_notebook`: Mostra qual está configurado atualmente.

---

## 4. Onde Salvar seus IDs

Recomendamos anotar seus IDs no arquivo `meus_notebooks.md` nesta pasta para fácil acesso.

Boa produtividade!
