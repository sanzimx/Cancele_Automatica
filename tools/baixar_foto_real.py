"""Baixa fotografia pública de exemplo e valida sua integridade."""
from pathlib import Path
import hashlib
import io
from urllib.request import Request, urlopen
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
URL="https://upload.wikimedia.org/wikipedia/commons/7/7e/1990-2018_Particular.jpg"
PAGE="https://commons.wikimedia.org/wiki/File:1990-2018_Particular.jpg"
EXPECTED_SHA1="dd7c1f0ea4a5ff8a67fb8d297dbb74ab0fb9308d"
CREDITS="""Fotografia: 1990-2018 Particular.jpg
Autor: JasonVogel1970
Data informada pelo autor: 12/09/2018
Fonte: https://commons.wikimedia.org/wiki/File:1990-2018_Particular.jpg
Arquivo original: https://upload.wikimedia.org/wikipedia/commons/7/7e/1990-2018_Particular.jpg
Licenca: Creative Commons Atribuicao-CompartilhaIgual 4.0 Internacional
https://creativecommons.org/licenses/by-sa/4.0/
Copia sem alteracoes. Recortes exportados devem preservar os creditos e a licenca.
Uso neste projeto: hipotese de teste OCR, sem acionamento fisico.
A foto nao demonstra autorizacao real do veiculo.
Nenhuma leitura correta ou desempenho foi presumido.
O rotulo esperado deve ser transcrito visualmente antes de avaliar o OCR.
"""
def download():
    folder=ROOT/"data_samples"/"foto_real"
    folder.mkdir(parents=True,exist_ok=True)
    destination=folder/"carro_placa_brasileira.jpg"
    (folder/"CREDITOS.txt").write_text(CREDITS,encoding="utf-8")
    if destination.exists():
        if hashlib.sha1(destination.read_bytes()).hexdigest()==EXPECTED_SHA1:
            return destination
        raise RuntimeError("Ja existe uma foto diferente nesse caminho. Ela foi preservada.")
    request=Request(URL,headers={"User-Agent":"CancelaAcademica/1.0 (educational image download)"})
    with urlopen(request,timeout=30) as response:
        data=response.read(5_000_001)
    if len(data)>5_000_000:
        raise RuntimeError("Resposta maior que o limite esperado.")
    if hashlib.sha1(data).hexdigest()!=EXPECTED_SHA1:
        raise RuntimeError("Foto diferente da versao consultada. Download nao foi instalado.")
    with Image.open(io.BytesIO(data)) as image:
        image.verify()
    # Criacao exclusiva evita sobrescrever um arquivo criado durante o download.
    with destination.open("xb") as stream:
        stream.write(data)
    return destination

if __name__=="__main__":
    print(download())
