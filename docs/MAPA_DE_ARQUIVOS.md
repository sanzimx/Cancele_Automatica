# Mapa dos arquivos internos
Para instalar e usar, siga COMECE_AQUI.html. Esta lista explica os componentes do programa.

| Arquivo | Responsabilidade | Execução manual necessária? |
|---|---|---|
| app.py | Interface, cadastro, fila de eventos e resultados | Não, usar iniciar.bat |
| ocr_service.py | Mantém modelos carregados em processo separado | Não |
| evaluate.py | Avaliação por manifesto CSV | Opcional, também acessível na interface |
| src/vision.py | Preparação, EasyOCR, normalização e tipos de parâmetros | Não |
| src/devices.py | Câmera e comunicação serial | Não |
| src/persistent_ocr.py | Gerencia o processo OCR persistente | Não |
| src/automatic_pipeline.py | Detector e leitura separada de várias placas | Não |
| src/specialized_ocr.py | Reconhecedor especializado de placas | Não |
| src/plate_retry.py | Tentativas adicionais de leitura no recorte | Não |
| src/reading_review.py | Diagnóstico e hipóteses por formato | Não |
| src/metrics.py | Cálculo das métricas | Não |
| tools/python_runtime.bat | Localiza/cria o Python do ambiente | Não, chamado pelos lotes principais |
| tools/preparar_projeto.py | Instalação e verificação por etapas | Não, chamado pelos lotes principais |
| tools/organizar_projeto.py | Arquivamento de sobras conhecidas e inventário | Não, chamado na inicialização |
| tools/verificar_detector.py | Preparação do modelo detector e verificação básica | Não |
| tools/ativar_ocr_especializado.py | Preparação do OCR e ativação local | Não |
| tools/gerar_amostras.py | Gera cenas sintéticas de demonstração | Somente se quiser regenerar amostras |
| tools/baixar_foto_real.py | Baixa a foto licenciada e valida a integridade | Não, botão Foto real |
| tools/gerar_casos_dificeis.py | Prepara versões escura/desfocada da foto | Não, botão Foto difícil |
| tools/gerar_apresentacao_pdf.py | Exporta a apresentação PDF | Opcional, para regenerar o documento |
| tools/empacotar.py | Cria ZIP para instalação em outra máquina | Não, usar gerar_pacote.bat |
| tests/ | Verifica regras e integrações com componentes simulados | Não, usar validar.bat |
| firmware/cancela_esp32/cancela_esp32.ino | Programa do ESP32 | Gravar depois pela Arduino IDE na etapa física |
| requirements.txt | Versões das dependências | Não, os lotes usam automaticamente |
| config.local.json | Cadastro e parâmetros deste computador | Editar preferencialmente pela interface |
| ocr_especializado.json | Ativação local do modelo | Gerado pela preparação do OCR |

Os arquivos __init__.py fazem parte da estrutura dos módulos e devem ser mantidos.
Materiais em arquivo/ são históricos, não componentes necessários para uma instalação nova.
O inventário local registra também arquivos adicionados pelo usuário que não aparecem neste mapa.
