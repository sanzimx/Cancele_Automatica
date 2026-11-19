# Reconhecimento mais rápido

## Alterações de 10/11/2026
- Trabalhador OCR persistente: EasyOCR/PyTorch carregam uma vez por sessão.
- O processo continua separado da interface e pode ser reiniciado após falha.
- Quantização continua desativada devido à instrução ilegal observada no computador.
- Largura padrão reduzida de 1280 para 640 pixels.
- canvas_size acompanha a largura OCR, decoder greedy, workers 0 e batch_size 1.
- Resultados temporários usam NPZ sem compressão.
- Threads CPU limitadas a até quatro, conforme os processadores lógicos disponíveis.
- O registro mostra o tempo total do pedido além da latência da pipeline.

## Configuração existente
Uma configuração salva anteriormente pode restaurar a largura antiga.
Na interface selecione 640 em Largura OCR, clique Aplicar parâmetros e depois Salvar cadastro e parâmetros.
Recorte a região para conter apenas a área de passagem da placa, sem cortar caracteres.
Se a placa pequena perder legibilidade, compare 960 ou 1280.
Confiança mínima regula aceitação, não é o principal controle de velocidade.

## Como medir
Reabra iniciar.bat. Analise a mesma foto três vezes.
Separe a primeira execução, que pode carregar modelos, das duas seguintes.
Registre o tempo da pipeline e o tempo total do pedido exibido no histórico.
Compare 640, 960 e 1280 usando as mesmas imagens e confira os textos reconhecidos.
Não reutilize tempos antigos como se fossem resultados da versão atual.
A configuração de threads é uma escolha inicial e não um ótimo medido para este computador.

## Limite da validação
Estas alterações foram revisadas por leitura. O terminal do ambiente de edição segue indisponível.
Não foi medida redução de tempo nem confirmada a precisão com os novos parâmetros.
O histórico anterior de cerca de 13 segundos é uma observação enviada pelo usuário na versão anterior.
