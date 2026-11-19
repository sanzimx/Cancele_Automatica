"""Casos controlados de degradação da fotografia real, sem alterar o texto da placa."""
from pathlib import Path
import cv2
import numpy as np
from tools.baixar_foto_real import download

def generate():
    original=download()
    image=cv2.imdecode(np.fromfile(str(original),dtype=np.uint8),cv2.IMREAD_COLOR)
    if image is None:
        raise RuntimeError("A foto original não pôde ser aberta.")
    folder=original.parent/"condicoes_dificeis"
    folder.mkdir(exist_ok=True)
    # Operações determinísticas para comparação com a mesma imagem original.
    dark=np.clip(image.astype(np.float32)*.35,0,255).astype(np.uint8)
    blurred=cv2.GaussianBlur(image,(11,11),2.5)
    combined=cv2.GaussianBlur(dark,(11,11),2.5)
    images={"escura.jpg":dark,"turva.jpg":blurred,"escura_e_turva.jpg":combined}
    for name,frame in images.items():
        path=folder/name
        if not path.exists():
            ok,encoded=cv2.imencode(".jpg",frame,[cv2.IMWRITE_JPEG_QUALITY,95])
            if not ok:
                raise RuntimeError("Falha ao preparar imagem de teste.")
            with path.open("xb") as stream:
                stream.write(encoded.tobytes())
    (folder/"CREDITOS_E_METODO.txt").write_text(
        "Derivados da fotografia 1990-2018 Particular.jpg, de JasonVogel1970.\n"
        "Fonte: https://commons.wikimedia.org/wiki/File:1990-2018_Particular.jpg\n"
        "Original preservado na pasta superior.\n"
        "Licenca da foto e destes derivados: CC BY-SA 4.0.\n"
        "https://creativecommons.org/licenses/by-sa/4.0/\n"
        "Alteracoes: escurecimento multiplicativo 0,35; desfoque gaussiano 11x11, sigma 2,5;\n"
        "e combinacao dos dois. Exportacao JPEG com qualidade 95.\n"
        "Derivados criados pelo codigo do projeto para avaliar robustez do OCR.\n"
        "Desfoque gaussiano nao reproduz todos os efeitos de movimento ou de uma camera real.\n"
        "O texto esperado da placa deve ser transcrito olhando a original, nao usando a saida OCR.\n"
        "Nao se presume que o sistema reconhecera as imagens degradadas.\n",
        encoding="utf-8")
    return folder/"escura_e_turva.jpg"

if __name__=="__main__":
    print(generate())
