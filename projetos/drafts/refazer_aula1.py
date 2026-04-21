import os
import subprocess
import time

NOTEBOOK_ID = "04f4aac0-924c-4803-8b28-9ae89cbcb30f"

focus_text = "Neste episódio de 25 a 30 minutos, vocês farão um Deep Dive sobre a 'Captura de Informação' no ecossistema Drafts, direcionado a um cirurgião oncológico super ocupado. Estruturem a conversa em quatro fases. Comecem (Iniciante) explicando por que o app sempre abre em branco e como isso elimina a fricção de anotar observações de um exame anatomopatológico. Em seguida (Intermediário), discutam como realizar o ditado de descrições cirúrgicas complexas via Apple Watch de forma nativa e como transições maiores de voz encontram o caminho pro Drafts. No modo (Avançado), abordem a concatenação de notas: como jogar o CID e histórico do plantão em um único draft central usando Ações prontas. Por fim, na fase (Mestre), conversem sobre o nível de programação, onde o cirurgião, que já usa o iTerm2 e ferramentas shell, pode enviar relatórios de sistema diretamente via linha de comando (CLI e scripts) para o Drafts. Foquem sempre na velocidade alucinante da ferramenta."

def run_cmd(cmd):
    return subprocess.run(f"source ~/.zshrc && {cmd}", shell=True, executable='/bin/zsh', capture_output=True, text=True)

print("=== Disparando Geração da Aula 1 (Retry) ===", flush=True)
run_cmd("nlm login switch default")

create_cmd = f"nlm audio create {NOTEBOOK_ID} --format deep_dive --length long --language pt-BR --focus \"{focus_text}\" --confirm"
print("Solicitando aos servidores do Google...", flush=True)
res = run_cmd(create_cmd)
if res.returncode != 0:
    print(f"Erro ao solicitar a fila do NLM: {res.stderr}")
    exit(1)

# Pega o ID na saída
artifact_id = None
for line in res.stdout.split('\n'):
    if "Artifact ID:" in line:
        artifact_id = line.split(":")[1].strip()

print(f"✅ Aula 1 aceita na fila de processamento! ID de rastreio: {artifact_id}", flush=True)

print("Iniciando contagem regressiva de 8 minutos para aguardar o NotebookLM gerar o conteúdo...")
for i in range(16):
    time.sleep(30)
    print(f"  ... { (i+1)*30 } / 480 segundos...", flush=True)
    
print("Tentando baixar a Aula 1 gora...\n")
output_path = "curso_drafts_audios/01_aula_captura.m4a"

if artifact_id:
    dl = run_cmd(f"nlm download audio {NOTEBOOK_ID} --id {artifact_id} --output \"{output_path}\"")
else:
    dl = run_cmd(f"nlm download audio {NOTEBOOK_ID} --output \"{output_path}\"")

if dl.returncode == 0:
    print("🎉 Aula 1 baixada com sucesso e pacote do curso Completo!")
else:
    print(f"❌ O Google ainda não terminou de gerar ou deu erro novamente. Tente o download depois com:\n nlm download audio {NOTEBOOK_ID} --id {artifact_id} --output \"{output_path}\"")
