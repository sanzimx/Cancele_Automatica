# Detector automático de várias placas
Atualização de 10/11/2026. Estas instruções complementam e atualizam a arquitetura inicial.

## Ativação no ambiente já instalado
1. Feche a interface.
2. Execute ativar_ocr.bat na raiz do projeto, com internet. O lote prepara detector e OCR.
3. Ele instala as dependências respeitando as versões de requirements.txt.
4. Carrega/baixa os pesos e faz inferência de verificação numa imagem vazia.
5. Executa os testes unitários. Um teste vazio não valida qualidade em carros.
6. Abra iniciar.bat e uma fotografia real.

Na interface mantenha Localizar placas automaticamente marcado.
Ao abrir uma foto real a busca volta à imagem inteira (ROI 0,0,100,100).
Foto exemplo desativa o detector: um cartão tipográfico não é uma fotografia real de placa.
Você pode desmarcar o detector para usar o OCR manual por região.

## Tecnologia e origem
Biblioteca open-image-models 0.6.0, de ankandrew:
https://github.com/ankandrew/open-image-models
https://pypi.org/project/open-image-models/0.6.0/

Modelo escolhido: yolo-v9-t-640-license-plate-end2end.
Execução ONNX Runtime 1.20.1 em CPU.
A biblioteca declara licença MIT. Preserve também os avisos específicos dos pesos distribuídos pelo projeto.
A instalação dos pesos usa os mecanismos da biblioteca. Não foi feita cópia dos pesos nesta edição.
As versões usadas e o nome do modelo são registrados em outputs/detector_info.json após a verificação local.
Métricas publicadas pelo autor não são resultados medidos neste projeto.

## Fluxo
1. A ROI define onde procurar, normalmente o quadro inteiro.
2. O detector localiza retângulos de placas, sem depender de detectar primeiro a carroceria.
3. As caixas voltam para as coordenadas originais da imagem.
4. Cada caixa ganha uma margem de 12% e é recortada antes do resize do OCR.
5. O LocalEngine aplica o processamento e o EasyOCR em cada recorte separado.
6. A interface desenha cada caixa e mostra seus resultados individuais no registro.
7. MULTIPLAS_PLACAS impede autorização global, mesmo se uma das placas for cadastrada.
8. SEM_PLACA indica ausência de detecção. SEM_LEITURA indica detecção sem OCR aceito.

O processo persistente mantém detector e OCR carregados entre análises.
A quantização do EasyOCR segue desativada por causa da falha nativa observada.
Carros, ônibus, caminhões e outros veículos podem ser testados, pois o alvo é a placa.
A implementação não garante cobertura uniforme de tipos de veículos ou países.

## Configurações
Confiança detector: filtro das detecções retornadas pelo modelo, separado da confiança OCR.
O processamento interno do modelo pode ter seu próprio limiar mínimo.
Largura OCR: tamanho de cada recorte para reconhecimento, não largura da cena inteira.
Busca distante: executa quadro inteiro e quatro janelas sobrepostas.
As janelas cobrem 62% da largura/altura da ROI e usam as suas quatro extremidades.
Detecções repetidas são removidas por IoU com limite 0,35.
Busca distante pode ajudar placas pequenas, mas executa mais inferências e pode aumentar falsos positivos.
Use a mesma coleção de fotos para comparar antes/depois.
Até 8 placas recebem OCR por pedido. Detecções adicionais aparecem em cinza e o limite é informado.
Mesmo com textos iguais, duas detecções distintas não são tratadas como um único veículo.

## Autorização
Cada leitura pode mostrar AUTORIZADO ou NEGADO como resultado individual.
Com várias placas na região, o resultado global é MULTIPLAS_PLACAS e não autoriza relé.
Para integrar uma cancela, configure uma ROI contendo somente a faixa/posição do veículo de entrada.
Ainda não há rastreamento de veículos entre quadros nem confirmação temporal por múltiplas leituras.
Esta atualização não implementa contagem de carros, marca/modelo ou reconhecimento de proprietários.

## Testes adicionados
tests/test_automatic.py usa detector e OCR simulados para testar:
- várias placas autorizadas, sem escolha indevida de uma;
- uma autorizada e outra ilegível;
- ausência de detecção sem fallback para autorizar texto solto;
- mapeamento da ROI para a foto original;
- busca em cinco janelas e supressão de duplicatas;
- confiança do detector;
- limites do recorte;
- OCR separado por placa;
- preservação da decisão de uma placa única.

A suíte não demonstra que a rede detecta placas reais.
Não foi possível executá-la no ambiente de edição porque o terminal falha antes de iniciar Python.
A ativação local executará a suíte e interromperá se houver falha.

## Validação real
Atualização de robustez: quando o OCR inicial retorna SEM_LEITURA, há até três tentativas por placa usando reconhecimento direto do recorte.
As variantes usam cinza integral, recorte sem os 22% superiores e contraste/nitidez moderados.
O cadastro não altera o texto reconhecido. Divergências entre candidatos acima do limiar produzem AMBIGUO.
As tentativas adicionais exigem escore de pelo menos 0,75, ou o limiar do operador se maior.
Esses escores não são probabilidades calibradas. As variantes são correlacionadas e não equivalem a observações independentes.
O histórico informa o tamanho da placa em pixels no arquivo original.
Essa atualização foi revisada por leitura e ainda precisa de validação local nas imagens problemáticas.

Teste fotos com 1, 2 e 3 veículos, inclusive um autorizado ao lado de um desconhecido.
Use imagens próximas, médias e distantes, com a placa ainda legível no arquivo original.
Registre caixas, texto esperado transcrito visualmente, resultados, tempo e parâmetros.
Compare Busca distante ligada/desligada e anote falsos positivos e placas não encontradas.
O avaliador CSV existente continua apropriado para casos com uma placa esperada.
Casos com várias placas exigem rótulos por placa e comparação individual; não use o CSV antigo para alegar recall multiveículo.
Sem anotações de caixas ainda não há medição de IoU, precisão ou recall do detector.
Fotos de baixa resolução, placas ocultas e caracteres sem detalhes continuam sendo limites físicos.

## Materiais da apresentação
O fluxo inicial apresentado nos slides deve ser atualizado para mostrar detector, recortes e OCR por placa.
O relatório deste documento descreve a atualização; a apresentação inicial não comprova esta nova execução.
Inclua capturas e medições locais depois de testar.
