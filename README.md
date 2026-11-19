# Cancela inteligente
Aplicação acadêmica de Computação Gráfica com detector de placas, OCR, interface desktop e integração serial com ESP32.

Repositório: https://github.com/sanzimx/Cancele_Automatica

## Baixar e instalar

No Windows, baixe e extraia o ZIP do GitHub ou use:

```bat
git clone https://github.com/sanzimx/Cancele_Automatica.git
cd Cancele_Automatica
instalar.bat
iniciar.bat
```

A instalação inicial precisa de internet para dependências e pesos. Não é necessário copiar a pasta .venv de outro computador.
O cadastro e os diagnósticos de cada instalação não fazem parte do repositório.

**Comece pelo [guia visual](COMECE_AQUI.html) ou pelo [passo a passo completo](docs/ENTREGA.md).**

## Comandos principais
| Arquivo | Quando usar |
|---|---|
| instalar.bat | Primeira instalação completa, inclusive em uma máquina nova |
| iniciar.bat | Uso diário |
| ativar_ocr.bat | Preparar ou atualizar detector e reconhecedor |
| validar.bat | Conferir sintaxe, dependências e testes |
| gerar_pacote.bat | Gerar ZIP para outro computador |

O instalador reutiliza o ambiente existente e preserva cadastro, fotos e resultados.
Na primeira instalação tenta obter Python 3.11 pelo launcher e instala as dependências exatas de requirements.txt.
São necessários Windows x64, Python 3.11 com Tcl/Tk e internet para preparar os modelos.
Se o launcher py não estiver instalado, instale Python 3.11 com esse componente antes de executar instalar.bat.
Não copie .venv entre computadores. Gere um pacote e execute instalar.bat no destino.

## Estrutura
| Caminho | Função |
|---|---|
| app.py | Interface e coordenação |
| ocr_service.py | Processo persistente do OCR |
| src/ | Aquisição, detector, reconhecedores, revisão e métricas |
| tools/ | Rotinas internas usadas pelos batches e pela interface |
| tests/ | Testes de regras, matemática e integrações simuladas |
| firmware/cancela_esp32/ | Código do ESP32 para a futura validação física |
| requirements.txt | Dependências fixadas, inclusive detector e OCR especializado |
| data_samples/ | Demonstrações e fotos de teste |
| docs/ | Documentação técnica, apresentação e orientações |
| outputs/ | Resultados, relatórios e diagnósticos locais |
| config.local.json | Cadastro e parâmetros deste computador, quando salvos |
| ocr_especializado.json | Ativação local do reconhecedor especializado |
| arquivo/ | Batches antigos e materiais de preparação preservados |
| dist/ | Pacote ZIP gerado para distribuição |

Não execute os lotes em arquivo/. O funcionamento atual usa os lotes padronizados na raiz.
Documentos técnicos datados preservam a evolução do projeto. Para comandos de instalação, siga COMECE_AQUI.html e docs/ENTREGA.md.

## Processamento
O detector YOLOv9 localiza placas e recorta a imagem original antes da leitura.
O EasyOCR faz a análise inicial. Se falhar e o recurso estiver ativado, o FastPlateOCR tenta o recorte.
O modo Veicular aplica os formatos brasileiros configurados. Identificadores permite texto alfanumérico livre de 3 a 10 caracteres.
Comparação com o cadastro é exata após normalização. Sugestões de formato não autorizam o relé.
Múltiplas placas na mesma região bloqueiam a autorização global.
O limiar escolhido na interface é respeitado; não existe piso oculto de confiança.
Os escores de modelos diferentes não representam probabilidades calibradas nem são diretamente comparáveis.

## Situação da validação
A análise funcional de fotos e redução de tempo nas execuções após a inicialização.
Não foram feitas medições independentes de acurácia nem validação física da cancela neste ambiente.
Em 19/11/2026, os 42 testes de regras passaram no ambiente local com Python 3.11.9, e pip check não encontrou conflitos.
Esses testes não substituem a instalação completa em uma máquina limpa, a avaliação do OCR em fotos reais ou os ensaios físicos.
Veja docs/VALIDACAO_2026-11-19.md para o escopo da verificação.
O inventário completo será produzido pela rotina local ao abrir iniciar.bat.
Arquivos desconhecidos são preservados e não são classificados automaticamente como inúteis.

## Documentação complementar
- [Entrega e passo a passo](docs/ENTREGA.md)
- [Detector automático](docs/DETECTOR_AUTOMATICO.md)
- [OCR especializado](docs/OCR_ESPECIALIZADO.md)
- [Plano de testes e métricas](docs/PLANO_DE_TESTES.md)
- [Créditos e uso de IA](docs/CREDITOS.md)
- [Revisão de leituras](docs/REVISAO_DE_LEITURAS.md)
- [Cadastro livre](docs/CADASTRO_LIVRE.md)

A equipe deve revisar, testar e compreender o código assistido por ChatGPT antes da defesa.
