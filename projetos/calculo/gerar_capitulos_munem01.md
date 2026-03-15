# Comandos para Geração de Áudios - Cálculo Munem-Foulis Vol. 1

Este documento lista os comandos necessários para utilizar o script `calculo_runner.py` e gerar os episódios em áudio do livro de Cálculo Munem-Foulis Volume 1 utilizando o NotebookLM.

Certifique-se de estar no diretório do projeto de cálculo antes de executar os comandos:
```bash
cd /Users/edsonmichalkiewicz/dev/notebooklm_michalk/calculo
```

## 1. Geração de Áudios (Criar)

Para iniciar o processo de requisição e criação de novos episódios no NotebookLM:

```bash
# Criar até 5 áudios sequencialmente (você pode alterar o número conforme a necessidade)
python3 calculo_runner.py --max-sections 5

# Iniciar a criação especificando exatamente os IDs das seções (ex: seções 1, 2 e 3)
python3 calculo_runner.py --sections 1,2,3
```

## 2. Status e Simulação

Úteis para acompanhar o progresso e testar antes de disparar muitas execuções:

```bash
# Ver o painel de status geral: mostra quais estão pendentes, criados ou baixados
python3 calculo_runner.py --status

# Simulação (dry-run): exibe quais seções seriam processadas sem gerar ou consumir nada
python3 calculo_runner.py --dry-run
```

## 3. Download de Áudios Prontos

Para baixar os episódios cujo processamento no servidor do NotebookLM foi concluído com sucesso:

```bash
# Baixa todos os áudios que estão com o status de "created" e prontos
python3 calculo_runner.py --download
```

> **Nota:** É recomendado aguardar cerca de 10 a 15 minutos após solicitar a criação antes de executar o comando de download.
