# Instalação, uso e preparação da entrega
Este é o guia atual dos batches padronizados. Substitui as instruções das versões corrigidas anteriores.

## 1. Instalar em uma máquina nova
1. Obtenha Cancela_Inteligente_Instalacao.zip, criado por gerar_pacote.bat.
2. Extraia a pasta cancela_final inteira para um local onde seu usuário possa gravar arquivos.
3. Tenha Windows x64, internet e o launcher Python disponível.
4. Execute instalar.bat.
5. Se Python 3.11 estiver ausente, o lote tentará py install 3.11.
6. Se o comando py não existir, instale Python 3.11 x64 com Tcl/Tk e o launcher, então repita instalar.bat.
7. Aguarde a criação de .venv, instalação de requirements.txt, preparação do detector e OCR.
8. O processo verifica dependências, sintaxe e testes. Gera amostras/PDF apenas se esses materiais estiverem ausentes.
9. Se alguma etapa falhar, a janela para e mostra onde buscar o registro. Não considere instalada uma etapa que falhou.
10. Quando concluir, execute iniciar.bat.

Não execute a instalação de dentro de uma janela de ZIP/WinRAR.
Não copie a pasta .venv de outra máquina.
Os modelos são baixados pela biblioteca durante a preparação e podem ficar no cache do usuário.
Esta distribuição requer internet na instalação inicial. Não foi preparado um instalador offline.
Não é necessário instalar Arduino IDE para analisar fotos. Ela será necessária para gravar o ESP32.

## 2. Usar na máquina já instalada
Execute iniciar.bat.
A rotina mantém cadastro, parâmetros, fotos e diagnósticos existentes.
Na abertura também arquiva sobras conhecidas e registra um inventário local.
Teste primeiro Foto exemplo. Depois use Abrir foto, Foto real ou Foto difícil.
Faça uma primeira análise para aquecer os modelos antes de comparar tempos.
Mantenha Autorizar pelo sensor desmarcado durante a simulação por fotos.

## 3. Ativar ou atualizar o OCR
Feche a interface e execute ativar_ocr.bat.
Esse lote instala as dependências previstas e prepara detector e OCR especializado.
Use-o se precisar preparar os modelos novamente, corrigir dependências ou ativar o recurso num ambiente antigo.
Na instalação nova bem-sucedida, instalar.bat já faz essa preparação.
Não precisa executar os dois a cada abertura do programa.

## 4. Validar a instalação
Feche a interface e execute validar.bat.
Ele verifica sintaxe Python, testes unitários e consistência das dependências.
Os registros ficam em outputs. Não depende de câmera ou ESP32.
A aprovação desses testes não comprova leitura correta em toda foto nem funcionamento elétrico.
Teste fotos reais, casos negativos e o circuito separadamente.

## 5. Transportar o programa para outro computador
Execute gerar_pacote.bat.
O arquivo será dist/Cancela_Inteligente_Instalacao.zip.
Ele inclui código, instaladores, dependências, testes, firmware, documentação e amostras controladas.
Exclui ambiente virtual, pesos/cache, cadastros, histórico, diagnósticos, fotos reais e arquivo antigo.
Não existe chave de câmera embutida no pacote. A senha é informada na interface.
No outro computador, extraia o ZIP e siga a primeira instalação.

## Mapa dos arquivos principais
| Arquivo/pasta | O que fazer |
|---|---|
| COMECE_AQUI.html | Abrir no navegador para ler o guia |
| LEIA_PRIMEIRO.txt | Ler orientações rápidas |
| instalar.bat | Executar uma vez para instalação completa |
| iniciar.bat | Executar para usar o programa |
| ativar_ocr.bat | Executar para manutenção do detector/OCR |
| validar.bat | Executar para registrar verificações |
| gerar_pacote.bat | Executar para criar o ZIP para outra máquina |
| app.py | Código principal, normalmente aberto por iniciar.bat |
| evaluate.py | Avaliação offline por CSV; também acessível na interface |
| ocr_service.py | Processo interno, não abrir manualmente |
| requirements.txt | Lista de versões, usada pelo instalador |
| src/ | Código interno, manter junto ao projeto |
| tools/ | Rotinas internas, manter junto ao projeto |
| tests/ | Testes, manter para reprodução |
| firmware/ | Manter para gravar e testar o ESP32 depois |
| data_samples/ | Abrir imagens pela interface |
| config.local.json | Não apagar se quiser manter cadastro/parâmetros |
| ocr_especializado.json | Ativação do OCR, criada pela preparação |
| outputs/ | Resultados e diagnósticos, consultar quando houver erro |
| arquivo/ | Histórico preservado, não executar os lotes antigos |
| docs/organizacao/ | Inventário e movimentações locais |
| dist/ | ZIP gerado para transportar o projeto |

## Organização e preservação
Os lotes antigos foram separados em arquivo/lotes_antigos.
O trabalhador antigo de OCR foi separado em arquivo/codigo_antigo.
O código ativo usa ocr_service.py e src/persistent_ocr.py.
A rotina organizar_projeto.py move somente caminhos antigos explicitamente conhecidos, sem excluir arquivos.
Se o destino já existe, cria outro nome em vez de sobrescrever.
Configuração, imagens, resultados, ambiente virtual e arquivos desconhecidos são preservados.
A raiz Projeto_de_pedro pode conter arquivos do usuário que o ambiente de edição não conseguiu listar.
O inventário deles será produzido localmente, sem declarar que tudo é descartável.

## Próxima etapa: cancela
Antes de integrar a parte física, confirmar placa, câmera, porta serial e firmware.
O firmware atual está em firmware/cancela_esp32/cancela_esp32.ino.
Os pinos estão registrados no código. A interface e o firmware usam protocolo com identificador de pedido.
Não misture o Python atual com o firmware antigo sem identificadores.
A validação de relé, sensor, botão e temporização ainda será feita na bancada.
O modo Identificadores continua destinado à simulação por foto; a autorização automática pelo sensor exige Veicular.
Um comando no relé não confirma a posição física de uma cancela.

## Situação desta organização
Os arquivos novos foram preparados e revisados por leitura.
O terminal do ambiente de edição falhou antes de executar Python, inclusive na tentativa de inventário.
Não foi possível executar os batches consolidados, criar o ZIP ou simular uma instalação limpa daqui.
O instalador e a rotina de inventário farão essas verificações localmente e registrarão seus resultados reais.
