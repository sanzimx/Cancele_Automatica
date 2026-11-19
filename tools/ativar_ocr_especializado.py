from pathlib import Path
import sys
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.specialized_ocr import SpecializedOCR,MODEL

if __name__=="__main__":
    print("Baixando/carregando OCR de placas: "+MODEL,flush=True)
    engine=SpecializedOCR()
    engine.load()
    root=Path(__file__).resolve().parents[1]
    (root/"ocr_especializado.json").write_text(json.dumps({"enabled":True,"model":MODEL}),encoding="utf-8")
    print("Modelo carregado. A qualidade nesta foto ainda precisa ser testada.")
