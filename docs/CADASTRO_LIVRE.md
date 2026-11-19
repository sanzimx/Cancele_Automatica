# Cadastro livre na simulação
Para preservar um identificador informado pelo operador que não corresponde ao formato veicular restrito,
selecione Modo: Identificadores ou clique Usar cadastro livre.
O texto normalizado pode ter de 3 a 10 letras/números e é comparado exatamente com o cadastro.
O detector automático e o OCR especializado passam a funcionar também nesse modo.
O modo Veicular continua validando ABC1234 e ABC1D23, sem modificar os dados informados.
As hipóteses orientadas pelo formato brasileiro são desativadas no modo livre.
Os limites de confiança continuam aplicados. Um texto cadastrado não torna uma leitura fraca aceitável.
A autorização física pelo sensor continua restrita ao modo Veicular na interface atual.
Esta alteração resolve o bloqueio de cadastro na simulação e não confirma o conteúdo de uma placa oficial.
Testes de comparação exata e baixa confiança foram acrescentados, mas não executados no ambiente de edição.
