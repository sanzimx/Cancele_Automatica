# Verificação para publicação no GitHub

Data: 19/11/2026.
Ambiente local: Windows, Python 3.11.9 no ambiente .venv existente.

- python -m unittest discover -s tests -v: 42 testes executados, todos aprovados.
- python -m pip check: nenhuma dependência inconsistente encontrada.
- Foram revisadas as exclusões de cadastro local, cache, ambiente virtual, históricos e arquivos antigos.

O teste cobre regras de OCR, confiança, formato, candidatos, coordenadas, métricas e detecção simulada de várias placas.
Não mede acurácia dos modelos em um conjunto real e não valida câmera, circuito, firmware compilado ou mecanismo físico.
A instalação completa em outro computador continua sendo uma verificação separada.

O workflow de testes usa somente as dependências dos testes de regras e não baixa pesos de OCR/detector.
