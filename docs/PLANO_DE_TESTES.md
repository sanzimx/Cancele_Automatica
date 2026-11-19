# Testes e obtenção das métricas
## Estado real
Preparado em 10/11/2026. Testes automatizados escritos, ainda não executados.
Não há resultados reais, vídeo gravado ou confirmação do circuito.
A falha do terminal de preparação impediu executar Python, compilar e renderizar materiais.

## Testes unitários
Comando na raiz:

    .venv\Scripts\python -m unittest discover -s tests -v

Guarde a saída em docs/evidencias_reais/testes.txt.
A suíte não testa a qualidade do modelo. Ela verifica regras e matemática de coordenadas.

## Conjunto sintético
Execute tools/gerar_amostras.py e avalie data_samples/manifesto_sintetico.csv.
Ele contém 6 imagens sintéticas criadas pelo próprio projeto.
O rótulo "test" desse conjunto só indica avaliação da fixture e não generalização para imagens reais.
Ajustes feitos observando essas imagens devem ser declarados.
Não use somente essas imagens para defender o desempenho final.

## Conjunto real proposto
Colete pelo menos 30 fotos autorizadas, sem publicar placas ou rostos de terceiros:
- 12 para configuração/validação, em pasta validacao.
- 18 para teste final, em pasta teste, sem usar essas fotos para escolher parâmetros.
- Inclua placas autorizadas e desconhecidas, cenas sem placa e texto OSD.
- Varie distância, luz, desfoque e inclinação, com pelo menos alguns casos difíceis.
- Imagens consecutivas do mesmo veículo/captura devem ficar no mesmo grupo para reduzir vazamento.
Os números acima são um plano de coleta, não uma exigência quantitativa do professor nem uma coleta já realizada.
Use cartões fictícios para preparar a bancada. Fotos de placas reais precisam de autorização e retenção limitada.

## Formato CSV
Crie um manifesto na mesma pasta-base das fotos:

    image,expected_plate,expected_authorized,condition,split
    teste/001.jpg,ABC1D23,1,frontal,test
    teste/002.jpg,XYZ9A88,0,distante,test
    teste/003.jpg,,0,sem_placa,test

A autorização esperada precisa corresponder ao cadastro configurado.
Placa em branco significa que não existe placa legível esperada naquela cena.
Uma foto com placa ilegível não deve receber texto adivinhado.
Identifique exclusões e revise os rótulos antes da execução.
Uma placa por ROI. Cenas com duas placas são casos de ambiguidade separados.

## Execução
Salve os parâmetros na interface. Clique Avaliar conjunto e selecione o CSV.
Alternativa:

    .venv\Scripts\python evaluate.py data_samples\manifesto_sintetico.csv --config config.local.json

Saída: outputs/avaliacao_DATA_HORA/ com métricas, CSV, relatório e imagens anotadas.
Nenhum comando de abertura é enviado durante a avaliação.

## Métricas
Acerto exato total = leituras idênticas aos rótulos / todos os casos, penalizando erros de execução.
Acerto exato positivo = leituras exatas / imagens com placa esperada.
CER positivo = soma das distâncias de Levenshtein / soma dos caracteres esperados nas imagens positivas.
Taxa de leitura falsa = negativas com texto de placa / total de negativas.
Acerto da decisão = decisões de autorização corretas / casos, penalizando erros de execução.
Autorizações falsas = casos não autorizados que o sistema autorizou.
Latência de pipeline = tempo de preparação + OCR + decisão.
Tempo médio e P95 usam casos da execução. Se houver erro, sua linha tem 0 ms e invalida interpretação do desempenho.
Download, inicialização, aquisição e serial não entram nesse tempo.
Zero autorizações falsas em uma amostra não prova ausência de risco em outros contextos.
Não há IoU ou mAP: o conjunto não possui caixas de verdade-terreno e o método não é detector treinado de placas.

## Ablação proposta
Na validação, compare confiança 0,40/0,60/0,80 e largura 640/1280.
Fixe os parâmetros escolhidos antes de executar o teste final.
Para comparar pré-processamentos, altere a pipeline em uma branch documentada e repita o mesmo conjunto de validação.
Não afirme que filtros melhoraram o resultado sem comparar medições.

## Ensaios físicos
| Caso | Ação | Esperado |
|---|---|---|
| Autorizada | Sensor + placa cadastrada | ID correspondente, verde, relé por 3 s |
| Desconhecida | Sensor + placa fora do cadastro | Vermelho, relé desligado |
| Sem placa | Sensor sem texto válido | Sem leitura, sem abertura |
| Ambiguidade | Duas placas na ROI | AMBIGUO, sem abertura |
| Timeout | Desligar aplicação após detecção | Negativa após 30 s |
| Mensagem atrasada | Enviar ID anterior | RESPOSTA_DESCARTADA |
| Botão | Pressionar durante OCR | Abertura manual, pedido cancelado |
| Sensor retido | Manter sensor ativo após ciclo | Sem repetir até liberar |
| USB removido | Desconectar ESP32 | Aviso, análise por foto disponível |
| Câmera ausente | Desconectar rede | Aviso e tentativa de reconexão |
| Arquivo inválido | Abrir arquivo não imagem | Aviso sem encerrar |
| Reinício | Reiniciar ESP32 | Relé inicia desligado |

Registre data, responsável, versão, esperado, observado e evidência.
A tabela descreve resultados esperados. Não é um registro de aprovação.
