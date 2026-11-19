# Relatório técnico
Atualização: a versão atual inclui detecção automática de placas. Consulte DETECTOR_AUTOMATICO.md, que atualiza as limitações e a arquitetura iniciais descritas abaixo.
## Identificação
Disciplina: Computação Gráfica. Professor: Pedro Cândido.
Tema: cancela com conferência visual de placas.
Integrantes, turma, datas da entrega e apresentação: a preencher pela equipe.

## Problema e escopo
Conferir se uma placa observada corresponde exatamente a um cadastro local e apresentar evidências visuais da decisão.
Entrada: foto, webcam ou câmera IP. Saída: texto, polígonos, status, tempo e registro local.
Usuário: operador de uma bancada demonstrativa. O acionamento físico é um relé de bancada.
A câmera não identifica a pessoa e a placa lida não comprova identidade ou legitimidade do veículo.

## Código inicial
O material recebido usa câmera HiLook por RTSP, EasyOCR em CPU, serial a 115200 bps, sensor IR e relé no ESP32.
O original analisa toda a imagem, mascara duas áreas OSD e aceita correspondência com textos curtos cadastrados.
Também concatena blocos sem verificar distância. O ESP32 usa delays e respostas sem ID.
A versão proposta introduz ROI, validação de formato, combinação geométrica limitada, interface e IDs por solicitação.

## Pipeline
Aquisição em thread mantém o último quadro recebido. Um pedido automático aguarda quadro recebido após o início da solicitação.
Pré-processamento: recorte da ROI, redimensionamento proporcional, conversão BGR/cinza, CLAHE e filtro bilateral.
O recorte reduz interferências. A escala padroniza largura. Cinza remove variação de canais.
CLAHE realça contraste em regiões locais. Bilateral busca reduzir ruído preservando bordas.
Essas operações precisam ser avaliadas: podem também degradar caracteres em condições específicas.
EasyOCR recebe a imagem preparada e allowlist alfanumérica.
Os resultados incluem quadrilátero, texto e escore. O código converte as coordenadas para a imagem original.

## Formação da hipótese e decisão
A normalização remove separadores e converte para maiúsculas.
Modo veicular exige três letras e quatro números, ou três letras, um número, uma letra e dois números.
Isso é uma restrição sintática. Não consulta base oficial nem identifica falsificação.
Blocos abaixo da confiança são rejeitados.
A união de até dois blocos considera alinhamento horizontal ou duas linhas próximas.
A menor confiança dos blocos compõe o escore da união.
Leituras repetidas são deduplicadas. Mais de uma hipótese distinta produz AMBIGUO.
A lista de autorizados não é usada para escolher a hipótese de OCR. A comparação é exata após a leitura.

## Coordenadas e desenho
Se a imagem original tem W por H e a ROI normalizada é (a,b,c,d):
x0 = inteiro(a W), y0 = inteiro(b H), x1 = inteiro(c W), y1 = inteiro(d H).
Após resize: sx = largura_processada/(x1-x0), sy = altura_processada/(y1-y0).
Um ponto OCR (u,v) volta para x = u/sx+x0, y = v/sy+y0.
O código arredonda e limita o resultado ao quadro.
Escalas independentes evitam erro acumulado por arredondamento da altura.
A interface usa thumbnail para manter a proporção na janela.
Azul indica ROI. Cinza indica texto. Verde indica autorização. Vermelho indica outros estados.
Os textos preservam compreensão por quem não diferencia as cores.
A saída sobreposta é uma cópia da imagem original.

## Interação e concorrência
A thread Tkinter manipula apenas widgets. OCR e carregamento dos pesos usam thread trabalhadora.
Uma fila transporta resultados para a interface.
A captura contínua evita acumular quadros no código Python.
A serial tem thread própria para leitura/escrita. Somente um OCR pode ocorrer por vez.
O preview após análise é congelado para examinar a evidência.
Uma nova análise com câmera solicita imagem nova em vez de reutilizar a evidência anterior.
Parâmetros e cadastro são obtidos antes da análise e usados como um conjunto fixo naquela execução.

## Protocolo serial
VEICULO_DETECTADO:boot-sequencia inicia uma transação.
AUTORIZADO:boot-sequencia e NEGADO:boot-sequencia são as respostas.
O ID inclui um valor de inicialização e um contador para reduzir colisões após reinicialização.
O firmware só aceita a resposta de uma transação pendente, dentro de 30 segundos.
Timeout, abertura manual e mudança de sessão tornam respostas antigas inválidas.
Não há confirmação de posição mecânica.
A comunicação serial não autentica criptograficamente o emissor.
A condição de bancada e o botão manual fazem parte do escopo demonstrativo.

## Máquina de estados
OCIOSO aguarda sensor liberado e posterior detecção.
AGUARDANDO mostra amarelo e aceita somente resposta do pedido.
ABERTO mantém relé por três segundos e sinal verde.
NEGADO mantém relé desligado, sinal vermelho e buzzer temporário.
Após ABERTO/NEGADO, o sensor precisa estar liberado antes de iniciar novo ciclo.
A temporização usa millis em vez de pausas bloqueantes.

## Falhas e recuperação
Câmera indisponível tenta reconectar com mensagens genéricas para não exibir senha.
Arquivo inválido produz aviso. Sem leitura ou ambiguidade não autoriza.
Serial desconectada mantém a interface disponível para testes.
Uma solicitação durante OCR ocupado é negada.
Os pesos exigem instalação e possível download inicial. Aquecer antes de habilitar o sensor.
Casos de avaliação que falham são registrados como erros e penalizam qualidade.
Erros de instalação das dependências não são ocultados pelo arquivo instalar.bat.

## Avaliação e evidências
A suíte unitária cobre formatos, desconhecidos, substrings, baixa confiança, distância entre blocos, ambiguidade, mapeamento e métricas.
Há um gerador de seis cenas sintéticas com rótulos.
A avaliação real deverá seguir o protocolo de docs/PLANO_DE_TESTES.md.
Os relatórios JSON e CSV mantêm configurações e resultados individuais.
Não foram medidas qualidade ou velocidade neste ambiente.
Os testes unitários e a compilação ainda precisam ser executados.
Nenhuma afirmação de aprovação foi inferida da existência dos testes.

## Limitações e próximos experimentos
Conjunto real pequeno não permite generalizar para ruas ou portarias.
A perspectiva não é corrigida. ROI não é detector automático de placa.
Falsos textos com formato veicular continuam possíveis.
O modo Identificadores serve para cartões de demonstração, sem autorização automática.
Ainda não há acompanhamento temporal entre vários quadros.
A escolha de confiança deve usar validação separada do teste final.
Este é um protótipo acadêmico. Uma instalação física com veículos precisaria de detecção de passagem, prevenção de esmagamento e projeto próprio de controle mecânico.

## Recursos externos e IA
EasyOCR, OpenCV, NumPy, Pillow, PySerial e PyTorch. Referências em CREDITOS.md.
Não utiliza VLM nem envia imagens para um modelo remoto.
ChatGPT apoiou revisão, programação, documentação e materiais didáticos.
A equipe deve registrar revisão executada, alterações próprias e limitações observadas.
