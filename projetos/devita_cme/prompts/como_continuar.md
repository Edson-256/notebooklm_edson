Para continuar:


# Ver status
python3 devita_cme/scripts/next_batch.py --status

# Próximo batch de 5
python3 devita_cme/scripts/next_batch.py --go

# Baixar todos os áudios pendentes de download
python3 devita_cme/scripts/download_audios.py

# Baixar capítulos específicos (ex: ch3, ch5, ch10)
python3 devita_cme/scripts/download_audios.py --chapters 3,5,10

# Verificar o que seria baixado sem executar (dry-run)
python3 devita_cme/scripts/download_audios.py --dry-run