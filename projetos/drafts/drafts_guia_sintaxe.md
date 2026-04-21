# Guia de Sobrevivência: Aprendendo a Sintaxe do Drafts (Fase Mestre)

Depois de entender a visão arquitetural e lógica ensinada pelos episódios Deep Dive, a execução técnica exigirá entender a sintaxe. Como você já tem background com n8n e outras plataformas lógicas, esse é o caminho rápido para domínio do código nativo do Drafts:

## 1. A Bíblia Técnica: Drafts Script Reference
O JavaScript dentro do Drafts não utiliza os comandos padrões de interação da web global (como DOM manipulation). Em vez disso, a fundação é feita através de objetos nativos poderosos que o criador manteve isolados.
Sua leitura de cabeceira para verificar propriedades deve ser o portal oficial:
**Acesse:** [scripting.getdrafts.com](https://scripting.getdrafts.com)
*Lá você encontrará a documentação essencial de classes como o `Draft()`, o gerador de telas interativas `Prompt()`, a classe `Workspace()` e, principalmente, a interface para chamadas webhooks: `HTTP()`.*

## 2. A Melhor Formação: Engenharia Reversa
No ecossistema do Drafts, quase ninguém inventa a roda do zero absoluto. A galeria aberta da comunidade hospeda soluções completadas prontas para dissecação.
**Acesse:** [directory.getdrafts.com](https://directory.getdrafts.com)
- **Método:** Identifique uma Action que chegue próximo ao que você precisa (como exportar arquivos, mandar pings para uma API).
- Instale a Action. Em seguida, clique em "Edit Action", encontre o degrau onde está "Script" e leia o código por si mesmo. Assistir e modificar fluxos pré-existentes é de longe o maior atalho para entender estruturas.

## 3. Utilizando IAs (LLMs) como Copilotos e Tradutores
Use a IA como aliada. As grandes LLMs conhecem toda a documentação oficial do Drafts e fóruns antigos. Se você sabe a lógica mas "travou" num detalhe formal de sintaxe, estruture o prompt assim:

> *"Estou programando dentro do aplicativo Drafts para Mac. Preciso de um Action Step em JavaScript usando as bibliotecas exclusivas do próprio Drafts. Quero que pegue a variável atual do corpo de texto selecionado `[[selection]]`, faça o parse para JSON, e utilize o objeto nativo `HTTP.create()` para emitir um POST simples no webhook do meu n8n."*

O modelo geralmente gerará o script adaptado e blindado contra possíveis falhas, poupando horas de busca cega na internet.

## 4. O "Console" Prático local no App
Antes de implementar códigos perigosos e apagar textos de exames vitais por engano, crie Workspaces focados somente em testes.
Construa Actions de "Rascunho" focadas apenas em um único Script box para ensaiar código com comandos como `console.log()` ou botões de `alert()`. Sempre abra e leia o log (Action Logs) nativo caso o step falhe. O Log do Drafts costuma ser bem claro onde, na linha exata, sua sintaxe desmoronou.
