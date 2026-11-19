# Diário de desenvolvimento
## Organização dos instaladores em 10/11/2026
Instalação consolidada em instalar.bat; uso diário por iniciar.bat; manutenção por ativar_ocr.bat e validar.bat.
Detector e OCR permanecem na instalação completa e podem ser preparados juntos pelo ativador.
Versões antigas foram preservadas em arquivo, sem remover configuração, ambiente ou dados do usuário.
Foi preparado gerar_pacote.bat para distribuição limpa e um guia COMECE_AQUI.html.
O inventário completo da raiz depende da execução local de iniciar.bat, pois o terminal de edição segue com falha.
Não houve validação de instalação limpa neste ambiente. A análise por fotos foi relatada como funcional por Samuel.

## 10/11/2026
Entrada: requisitos da disciplina e os dois códigos de Samuel.
Análise: câmera RTSP e leitura serial já estruturadas. OCR sobre cena inteira e concatenação sem geometria.
Decisões: Tkinter local, EasyOCR em CPU, ROI ajustável, formatos de placa, avaliação offline e protocolo com ID.
Implementação preparada: módulos, interface, firmware não bloqueante, testes e documentação.
Revisão estática: corrigida reutilização de foto anterior em análises de câmera e filtradas mensagens de sessões seriais antigas.
Limitação: terminal do ambiente falhou por ausência de System.Memory 10.0.0.0 antes da execução.
Não houve execução de testes, compilação do firmware ou medição.
Responsável pela elaboração assistida: ChatGPT com material fornecido por Samuel.
Integrantes responsáveis por revisão e execução: registrar após a atividade.

## Próximo registro real
Data:
Integrante:
Arquivo/funcionalidade:
Teste executado:
Resultado observado:
Commit/evidência:
