# Fontes, licenças e declaração de IA
Atualização do detector: open-image-models 0.6.0 (ankandrew), modelo yolo-v9-t-640-license-plate-end2end e ONNX Runtime 1.20.1.
Fontes: https://github.com/ankandrew/open-image-models e https://onnxruntime.ai/.
O código da biblioteca declara MIT. Os pesos são obtidos pelo mecanismo do projeto e devem conservar seus próprios avisos.
Os índices publicados pelo autor não foram tratados como métricas desta aplicação.
Consulta documental: 10/11/2026. Não foram baixados ou redistribuídos pesos nesta entrega.

## Origem do trabalho
- Enunciado: Projeto_Final_Visao_Computacional_Inteligencia_Multimodal_30_Pontos.docx, professor Pedro Cândido.
- Orientação complementar da atividade: Markdown colado(1).md.
- Base: sistema_cancela.py e cancela_esp32.ino fornecidos por Samuel.
- Adaptação: interface, organização, avaliação, protocolo e documentação elaborados com auxílio do ChatGPT.
- As amostras geradas por tools/gerar_amostras.py usam texto e formas sintéticas criadas pelo projeto.
- Sem fotografias externas, sem VLM, sem API de reconhecimento remoto.

## Software
| Recurso | Uso | Fonte e licença |
|---|---|---|
| EasyOCR 1.7.2 | Detecção de texto e reconhecimento | https://github.com/JaidedAI/EasyOCR • Apache-2.0 |
| OpenCV | Captura, filtros e desenho | https://opencv.org/license/ • Apache-2.0 nas versões recentes |
| PySerial | Comunicação USB serial | https://github.com/pyserial/pyserial/blob/master/LICENSE.txt • BSD-3-Clause |
| NumPy | Arrays e leitura de bytes | https://numpy.org/ e licença da versão instalada |
| Pillow | Exibição de imagens no Tkinter | https://github.com/python-pillow/Pillow/blob/main/LICENSE |
| PyTorch e Torchvision | Execução do EasyOCR | https://github.com/pytorch/pytorch e https://github.com/pytorch/vision |
| Python e Tkinter | Aplicação e interface | https://docs.python.org/3/library/tkinter.html |
| Arduino core ESP32 | Firmware | https://github.com/espressif/arduino-esp32 |

Preserve as licenças das dependências instaladas. A tabela não substitui seus textos legais.
O EasyOCR pode obter detector CRAFT e reconhecedor inglês por sua distribuição padrão.
Registre os nomes/versões/hash dos arquivos efetivamente usados antes da entrega.
Não se presumiu que a licença do código cubra automaticamente todos os pesos ou dados de treinamento.

## Referências técnicas
- EasyOCR API: https://jaided.ai/easyocr/documentation/
- EasyOCR tutorial: https://www.jaided.ai/easyocr/tutorial/
- OpenCV processamento: https://docs.opencv.org/4.x/d7/dbd/group__imgproc.html
- Filtro bilateral: https://opencv.org/image-filtering-using-convolution-in-opencv/
- Serial: https://pyserial.readthedocs.io/en/latest/pyserial.html

## Registro do uso de IA
Ferramenta: ChatGPT, nesta conversa.
Finalidades: análise dos arquivos recebidos, proposta da arquitetura, elaboração de código, testes, documentação e apresentação.
Partes afetadas: todos os arquivos novos do pacote.
Revisão realizada nesta preparação: inspeção do código e consistência com o enunciado.
Revisão ainda necessária: execução da suíte, teste das dependências, validação do OCR e teste da bancada.
A equipe não deve apresentar código gerado como autoria humana exclusiva nem atribuir compreensão não demonstrada a integrantes.

## Dados e retenção
Senha da câmera: somente memória da aplicação.
Cadastro local e outputs: fora do Git.
Fotografias reais: obter autorização, minimizar enquadramento de terceiros e apagar após o prazo combinado.
A aplicação só salva a fotografia quando o operador pede evidência ou executa avaliação.
O histórico CSV registra placa e decisão. Deve ter acesso restrito e descarte definido.
