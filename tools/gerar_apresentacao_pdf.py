"""Gera apresentação PDF em paisagem. Execute após instalar requirements.txt."""
import json
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
ROOT=Path(__file__).resolve().parents[1]
SLIDES=json.loads(r'''[["Cancela inteligente","Reconhecimento de placas com Python e ESP32","Computação Gráfica • Professor Pedro Cândido","Protótipo acadêmico • Samuel e equipe a identificar"],["Problema e resultado esperado","Conferência visual de acesso","A câmera observa uma placa. O sistema reconhece o texto e consulta um cadastro local.","A interface apresenta a leitura e a decisão. O ESP32 aciona um relé quando recebe autorização válida."],["Escopo da demonstração","Foto, câmera e bancada","Foto ou câmera IP/webcam como entrada. EasyOCR local em CPU.","O sistema usa uma região de interesse configurada pelo operador. Não possui detector treinado especificamente para placas.","Não há VLM ou envio de imagens para uma API."],["Arquitetura","Uma solicitação por detecção","ESP32 envia um identificador quando o sensor detecta presença.","Python captura um quadro novo, processa a região e reconhece os caracteres.","A resposta contém o mesmo identificador. O firmware rejeita respostas vencidas."],["Pré-processamento","Preparação da região visual","Recorte da região de interesse e escala proporcional.","Conversão para cinza e realce local de contraste com CLAHE.","Filtro bilateral para reduzir ruído. O efeito desses ajustes precisa de comparação experimental."],["Reconhecimento","Texto e hipóteses de placa","EasyOCR retorna quadriláteros, texto e escores.","O código filtra confiança, aplica formatos ABC1234 ou ABC1D23 e considera a proximidade de até dois blocos.","Duas hipóteses distintas geram ambiguidade. Cadastro não corrige nem escolhe a leitura."],["Computação Gráfica","Mapeamento e representação","A ROI transforma porcentagens em coordenadas da imagem.","x = u / sx + x0    e    y = v / sy + y0","A sobreposição desenha polígonos e rótulos. A interface preserva proporção e permite comparar original, processada e resultado."],["Interface e interação","Parâmetros sem editar código","Confiança mínima, largura OCR, contraste e região de leitura.","Cadastro de autorizados e seleção de entrada.","Cores com legenda textual, exportação de evidências e avaliação em lote."],["Integração física","Controle por estados","Pinos mantidos do projeto original: IR 21, relé 25, botão 19, LEDs 4/22/23 e buzzer 5.","Estados: ocioso, aguardando, acionado e negado. Temporização sem delay bloqueante.","Relé acionado por três segundos. Não há sensor que confirme a posição de uma cancela."],["Método de avaliação","Qualidade e desempenho","Acerto exato e taxa de erro por caractere nas imagens positivas.","Leituras falsas em cenas negativas, acerto da decisão e autorizações falsas.","Tempo médio e P95 da pipeline. Captura, download e serial ficam fora desse tempo."],["Resultados e evidências","Implementação preparada, medições pendentes","Código, testes, avaliação, documentação e geração de amostras foram preparados.","Não houve execução neste ambiente devido a falha do terminal. Não há taxas de acerto ou tempos medidos.","Após a execução local, inserir resultados do CSV/JSON, exemplos de acertos e erros e configuração do computador."],["Limitações","Erros que a equipe precisa demonstrar","Perspectiva, reflexo, desfoque, baixa luz e caracteres pequenos podem impedir a leitura.","Textos de fundo com formato de placa podem gerar falsos candidatos.","Amostras sintéticas verificam casos controlados. Imagens reais autorizadas são necessárias para avaliar o uso pretendido."],["Evolução, autoria e créditos","Do código recebido à versão organizada","Base: sistema_cancela.py e cancela_esp32.ino fornecidos por Samuel.","Novos recursos: interface, ROI, geometria dos blocos, IDs, avaliação e documentação.","ChatGPT auxiliou na elaboração. Cada integrante deve executar, revisar e explicar suas contribuições. Fontes no documento de créditos."],["Demonstração e encerramento","Evidências para a defesa","Mostrar uma leitura autorizada, uma desconhecida e uma cena sem placa.","Comparar original e processada. Explicar um parâmetro e um exemplo de erro.","Apresentar métricas reais e, após validar o circuito, o ciclo completo com sensor e relé."]]''')
def main():
    output=ROOT/"docs"/"APRESENTACAO.pdf"
    c=canvas.Canvas(str(output),pagesize=(960,540))
    c.setTitle("Cancela inteligente - Computação Gráfica")
    c.setAuthor("Samuel e equipe - elaboração assistida por ChatGPT")
    for index,slide in enumerate(SLIDES,1):
        dark=index==1
        c.setFillColor(HexColor("#142b40" if dark else "#f8fafc"))
        c.rect(0,0,960,540,fill=1,stroke=0)
        c.setFillColor(HexColor("#6dd3c4" if dark else "#246a77"))
        c.setFont("Helvetica",13)
        c.drawString(52,486,slide[0].upper())
        c.setFillColor(HexColor("#ffffff" if dark else "#142b40"))
        c.setFont("Helvetica-Bold",32)
        y=435
        for line in simpleSplit(slide[1],"Helvetica-Bold",32,850):
            c.drawString(52,y,line); y-=39
        y-=20
        c.setFont("Helvetica",20)
        for paragraph in slide[2:]:
            for line in simpleSplit(paragraph,"Helvetica",20,850):
                if y<65:
                    raise ValueError("Texto excede o slide "+str(index))
                c.drawString(52,y,line); y-=28
            y-=16
        c.setFillColor(HexColor("#cad7e2" if dark else "#526777"))
        c.setFont("Helvetica",10)
        c.drawString(52,25,"Computação Gráfica - Cancela inteligente")
        c.drawRightString(908,25,f"{index:02} / {len(SLIDES)}")
        c.showPage()
    c.save()
    print(output)
if __name__=="__main__":
    main()
