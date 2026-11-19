# Correção do limiar da interface
O OCR especializado e as tentativas adicionais impunham um piso de 0,75,
mesmo quando o operador selecionava um limite menor na interface.
Esse piso foi removido. Todos os reconhecedores respeitam a Confiança mínima configurada.
O filtro de formato e a comparação exata ao cadastro continuam separados.
Exemplo de regra: escore 0,479 passa com limite 0,40 e falha com limite 0,60.
Isso verifica consistência da decisão, não comprova correção do texto reconhecido.
Um limiar menor aceita mais leituras fracas e precisa de avaliação com exemplos corretos e incorretos.
O modo Identificadores permanece destinado à simulação sem autorização automática pelo sensor.
Esta correção substitui as referências anteriores a um piso fixo de 0,75 na documentação.
Foram escritos testes para os dois limites. Não executados aqui porque o terminal segue indisponível.
