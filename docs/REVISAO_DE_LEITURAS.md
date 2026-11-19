# Revisão geral das leituras

Esta versão separa texto reconhecido, validade de formato e autorização.
Uma leitura rejeitada não aparece mais como se o OCR tivesse produzido escore zero.
O texto bruto e o escore original são exibidos com FORMATO_INVALIDO ou BAIXA_CONFIANCA, conforme o caso.
Esses resultados permanecem sem autorização automática.

## Hipóteses sem substituições fixas
O reconhecedor especializado passa a usar cct-s-v2-global-model.
A sessão ONNX é encapsulada somente para capturar suas saídas completas, sem alterar a inferência.
Para as hipóteses, o código compara os escores de todos os caracteres do alfabeto em cada posição.
Considera os esquemas brasileiros LLLDDDD e LLLDLDD.
Busca as melhores sequências por soma dos logaritmos dos escores.
Mantém o escore de cada alternativa: a hipótese não herda o escore da letra originalmente escolhida.
Nenhum código de placa, lista de confusões ou cadastro de autorizados orienta a geração de hipóteses.
Não é solução universal para outros países, caracteres apagados ou qualquer qualidade de imagem.
As hipóteses são somente para revisão e não alteram a placa aceita nem comandam o relé.
Saídas incompatíveis com a API/tamanho esperado são informadas e não geram probabilidades inventadas.

## Ativação e validação
Feche a interface e execute ativar_ocr.bat para preparar o novo modelo. Na instalação nova, instalar.bat já faz isso.
Reabra iniciar.bat e teste as mesmas fotos. Mantenha o limiar de confiança para comparar.
O instalador executa os testes de regras e interrompe se houver falha.
No ambiente de edição, o terminal ainda falha antes de iniciar Python. Os novos testes não foram executados aqui.
Registre leituras corretas, incorretas, rejeitadas, tempo e nomes dos modelos usados.
Não conte uma hipótese visualmente plausível como acerto automático do sistema.

Fontes da API:
https://ankandrew.github.io/fast-plate-ocr/latest/reference/inference/inference_class/
https://github.com/ankandrew/fast-plate-ocr
