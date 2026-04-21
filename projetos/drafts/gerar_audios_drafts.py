import os
import subprocess
import time
import sys

NOTEBOOK_ID = "04f4aac0-924c-4803-8b28-9ae89cbcb30f"

prompts = [
    {
        "lesson": 1,
        "name": "01_aula_captura.m4a",
        "focus": "Neste episódio de 25 a 30 minutos, vocês farão um Deep Dive sobre a 'Captura de Informação' no ecossistema Drafts, direcionado a um cirurgião oncológico super ocupado. Estruturem a conversa em quatro fases. Comecem (Iniciante) explicando por que o app sempre abre em branco e como isso elimina a fricção de anotar observações de um exame anatomopatológico. Em seguida (Intermediário), discutam como realizar o ditado de descrições cirúrgicas complexas via Apple Watch de forma nativa e como transições maiores de voz encontram o caminho pro Drafts. No modo (Avançado), abordem a concatenação de notas: como jogar o CID e histórico do plantão em um único draft central usando Ações prontas. Por fim, na fase (Mestre), conversem sobre o nível de programação, onde o cirurgião, que já usa o iTerm2 e ferramentas shell, pode enviar relatórios de sistema diretamente via linha de comando (CLI e scripts) para o Drafts. Foquem sempre na velocidade alucinante da ferramenta."
    },
    {
        "lesson": 2,
        "name": "02_aula_organizacao.m4a",
        "focus": "Mergulhem de 20 a 30 minutos no conceito de organização fluida de dados usando Workspaces e Tags do Drafts. O ouvinte primário é um cirurgião oncológico acostumado a lidar com milhares de rascunhos fragmentados, de planilhas até diários de condutas oncológicas. A discussão deve ter progressão em 4 fases. Fase 1 (Iniciante): Arquivo vs Caixa de Entrada. Por que arquivar não apaga. Fase 2 (Intermediário): A estruturação de Workspaces paralelos: construam a narrativa de trocar entre a configuração do 'Consultório' para a ferramenta hiper-limitada do 'Bloco Cirúrgico'. Fase 3 (Avançado): A busca poderosa (Regular Expressions em buscas nativas) cruzando sintomas, tags retrospectivas e organização em lote. Fase 4 (Mestre): A parte de código/scripts da própria organização. Como uma automação Javascript customizada interna poderia varrer os drafts sem ler pastas, achar siglas como 'TNM' ou 'ECOG' e aplicar tags de forma silente na própria camada nativa."
    },
    {
        "lesson": 3,
        "name": "03_aula_templates.m4a",
        "focus": "Entreguem um conteúdo de 25 minutos com ritmo alto sobre a Engine de Formatação Textual avançada do Drafts e seu uso na rotina clínica médica. O alvo domina ferramentas robustas de edição, é cirurgião e adora otimização de tempo com teclados rápidos. Progressão obrigatória em 4 fases. Fase 1 (Iniciante): Extensões úteis do teclado virtual nativo para médicos e utilidade fundamental do visualizador de Markdown renderizado para laudos PDF rápidos. Fase 2 (Intermediário): Engine de formatação, onde variáveis do tipo 'data e hora formatadas' fundem-se em esqueletos de e-mails para relatar intercorrências sem perda tática. Fase 3 (Avançado): Prompt Steps no Drafts. Pensem na cena interativa: o médico está escrevendo um resumo, dispara um atalho e o Drafts invoca janelas de prompt pedindo dados de drenagem e injeta isso perfeitamente, anulando a necessidade de formulários longos. Fase 4 (Mestre): Script steps tratando textos. Retirem dados brutos estruturados e utilizem funções Javascript embutidas de Regex e Match Groups do Drafts Action script para substituir IDs confusos por links legíveis aos pacientes corporativamente."
    },
    {
        "lesson": 4,
        "name": "04_aula_roteamento.m4a",
        "focus": "O papo agora será técnico e visionário numa conversa de até 30 minutos sobre Roteamento Integrado de Textos e Automações complexas, tendo sempre o Médico Cirurgião com perfil nerd e frot-end de Jotforms em mira. Progressão em 4 atos, do simples ao mestre. Fase 1 (Iniciante): Expliquem as Actions prontas disparando atalhos corriqueiros mas de alta frequência pros app Reminders e Apple Calendar na pressa comanda clínica. Fase 2 (Intermediária): Arquivamento técnico. Como pegar uma pesquisa longa e, com um botão, convertê-la em arquivo .MD com headers perfeitos sincronizado à pasta do Vault do Obsidian que monitora as pesquisas médicas dele e referências. Fase 3 (Avançada): x-callback-urls. Mostrando o encadeamento de chamadas invisíveis entre e-mails da enfermaria mandando IDs via URL pra preencher esquemas do DevonThink e planners. Fase 4 (Mestre): O ápice. Como desenhar uma WebHook Request scriptada: o clique silencioso de uma ação num iPad cru joga todo o histórico formatado pra dentro da nuvem do seu roteador on premise (ex: n8n) acionando pipelines massivas de banco de dados e enviando e-mails à clinica sobre o plano do bloco cirúrgico. Tudo do zero e codado lá mesmo."
    },
    {
        "lesson": 5,
        "name": "05_aula_ai_scripts.m4a",
        "focus": "No episódio que fecha o ciclo educacional profundo com cerca de 30 minutos, o assunto é Inteligência Artificial pura associada à programação no ambiente de texto raiz. A audiência é exatamente o cirurgião muito acostumado com tecnologia de vanguarda que agora usará o Drafts como intermediador AI. Escalem de novo: Fase 1 (Iniciante): As 'Actions prontas' do diretório: a tradução simplificada de textos clínicos via botões base da OpenAI e como dispensam o browser para ganhos absurdos de agilidade. Fase 2 (Intermediário): Como construir Prompts no System e formatar respostas nativas combinando com tags como Data e tags originais ('[[draft]]'), modelando a persona AI como Oncologista Sênior em background. Fase 3 (Avançada): O Action Group: o incrível efeito dominó de usar um bloco longo preenchido que varre os dados pra inteligência da AI, que filtra, separa laudos perigosos e em sequência cria um roteamento editado que limpa textualmente a caixa original daquele Draft de forma interativa até ser guardado finalizado. Fase 4 (Mestre): Uma conversa sobre os porões do app. A capacidade nativa do Drafts de programar via Engine Javascript para acessar assincronamente as APIs de IAs mais pesadas, ler os tokens individualmente e guardar e repassar credentials customizados gerenciados pela própria central. Ressaltem as incríveis habilidades cognitivas disponíveis assimilar fluxos médicos super massivos via manipulação de objetos lógicos."
    }
]

def run_cmd(cmd):
    print(f"Executando: {cmd}", flush=True)
    process = subprocess.run(f"source ~/.zshrc && {cmd}", shell=True, executable='/bin/zsh')
    return process

os.makedirs("curso_drafts_audios", exist_ok=True)

print(f"Iniciando batelada de {len(prompts)} aulas...", flush=True)

for p in prompts:
    print(f"\\n{'='*50}", flush=True)
    print(f"Iniciando Geração da Aula {p['lesson']}/5...", flush=True)
    
    focus_text = p['focus'].replace('"', '\\"') 
    create_cmd = f"nlm audio create {NOTEBOOK_ID} --format deep_dive --length long --language pt-BR --focus \"{focus_text}\" --confirm --profile default"
    
    res = run_cmd(create_cmd)
    
    if res.returncode != 0:
        print(f"Falha na geração do áudio {p['lesson']}. Abortando.", flush=True)
        sys.exit(1)
        
    print(f"Aguardando 8 minutos para a geração da Aula {p['lesson']}...", flush=True)
    for i in range(16):
        time.sleep(30)
        print(f"  ... {i*30}/480 segundos...", flush=True)
        
    print(f"Download da Aula {p['lesson']}...", flush=True)
    output_path = f"curso_drafts_audios/{p['name']}"
    dl_cmd = f"nlm download audio {NOTEBOOK_ID} --output \"{output_path}\""
    run_cmd(dl_cmd)
    
    print(f"Aula {p['lesson']} salva com sucesso em {output_path}!", flush=True)

print("\\n✅ Todas as aulas concluídas e baixadas!", flush=True)
