Como usar

  cd projetos/Lehninger

  # Começar pelas 10 seções mais relevantes para oncologia
  python3 lehninger_runner.py --priority high --max-sections 10

  # Depois de ~15min, baixar os prontos
  python3 lehninger_runner.py --download

  # Capítulo específico (ex: Biosignaling)
  python3 lehninger_runner.py --chapter 12

  # Ver progresso
  python3 lehninger_runner.py --status

  Os slide prompts já estão em slides/ — cada um referencia explicitamente a estrutura do áudio
  correspondente (mesmo formato, mesmos segmentos) para manter a sincronia.
