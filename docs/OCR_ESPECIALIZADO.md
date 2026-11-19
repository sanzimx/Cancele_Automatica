# OCR específico de placas
Execute ativar_ocr.bat com a interface fechada e conexão à internet. Em máquina nova, instalar.bat já prepara tudo.
A instalação é adicional, preserva as versões das dependências principais e ativa o modelo depois que ele carrega.
Reabra iniciar.bat e analise a mesma fotografia. Não é necessário alterar o cadastro para ler uma placa.

Biblioteca: fast-plate-ocr 1.1.0 (MIT).
Modelo atual: cct-s-v2-global-model, executado em CPU pelo ONNX Runtime.
Após atualizar o modelo, execute ativar_ocr.bat para preparar os novos pesos.
Fontes: https://github.com/ankandrew/fast-plate-ocr
https://ankandrew.github.io/fast-plate-ocr/latest/inference/running_inference/
Preserve os avisos dos pesos obtidos pela biblioteca.

O novo reconhecedor é uma alternativa quando o EasyOCR retorna SEM_LEITURA em uma placa detectada.
Recebe o recorte original sem CLAHE, filtro bilateral ou nitidez adicional.
A biblioteca prepara o modo de cor e a entrada exigidos pelo modelo.
O escore exibido é o menor escore por caractere alfanumérico.
É exigido pelo menos 0,75, ou o limiar do usuário se maior, além de formato veicular válido.
Não é uma probabilidade calibrada de acerto da placa nem é diretamente comparável ao escore do EasyOCR.
O texto reconhecido é comparado exatamente ao cadastro. Não há substituição guiada por placa autorizada.
O mecanismo de várias placas continua impedindo autorização global.

O arquivo ocr_especializado.json ativa este recurso. Para desativar, altere enabled para false e reabra a interface.
O reconhecedor segue carregado entre análises na mesma sessão.
Ainda não houve execução deste modelo no ambiente de edição por falha do terminal.
Testes de regras foram escritos. O instalador os executa localmente.
A imagem enviada pelo usuário não foi transformada em rótulo confirmado a partir de um palpite visual.
Compare os resultados da mesma fotografia com o modelo antigo e com o especializado e registre eventuais erros.
