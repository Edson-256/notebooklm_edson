import os
import subprocess

NOTEBOOK_ID = "04f4aac0-924c-4803-8b28-9ae89cbcb30f"

# IDs que eu recuperei dos logs quando o gerador enfileirou todos com sucesso agorinha
audios = [
    { "lesson": 1, "name": "01_aula_captura.m4a", "id": "72a2816b-03c4-4e56-81f3-e0e804c89d78", "tema": "Captura Automática e iTerm2" },
    { "lesson": 2, "name": "02_aula_organizacao.m4a", "id": "442b9fa1-cb6a-4642-979d-9c5a5258b78f", "tema": "Workspaces e Filtros com Regex" },
    { "lesson": 3, "name": "03_aula_templates.m4a", "id": "68e07896-84c3-43fa-8275-587cadd222b6", "tema": "Engine de Templates e Markdown PDF" },
    { "lesson": 4, "name": "04_aula_roteamento.m4a", "id": "c589352a-a902-42e7-8d8b-daf81c23e906", "tema": "Roteamento Avançado e Webhooks pro n8n" },
    { "lesson": 5, "name": "05_aula_ai_scripts.m4a", "id": "1c7b360e-7a69-4737-b891-a319abc8e505", "tema": "Automação com IA Natively Integrated" }
]

def run_cmd(cmd):
    return subprocess.run(f"source ~/.zshrc && {cmd}", shell=True, executable='/bin/zsh', capture_output=True, text=True)

os.makedirs("curso_drafts_audios", exist_ok=True)
falhas = []

print("=== Recuperando Áudios Concluídos ===")
run_cmd("nlm login switch default")

for a in audios:
    print(f"Verificando status: Aula {a['lesson']} - {a['tema']}...")
    output_path = f"curso_drafts_audios/{a['name']}"
    dl_cmd = f"nlm download audio {NOTEBOOK_ID} --id {a['id']} --output \"{output_path}\""
    
    res = run_cmd(dl_cmd)
    
    if res.returncode == 0:
        print(f" ✅ Sucesso na extração!")
    else:
        print(f" ❌ Arquivo inexistente/Falha interna do Google.")
        falhas.append(a)

print("\n" + "="*50)
if len(falhas) == 0:
    print("Inacreditável. Todas as 5 aulas foram geradas e estão salvas!")
elif len(falhas) == 1:
    f = falhas[0]
    print(f"O Mistério foi desvendado: A aula que está acusando o selo vermelho no seu painel é a Aula {f['lesson']} (Tema: {f['tema']}).")
    print(f"As outras {5 - len(falhas)} aulas já foram salvas em formato m4a na pasta 'curso_drafts_audios' e você já pode ouví-las.")
else:
    print(f"Parece que mais de um falhou: {[f['lesson'] for f in falhas]}")
