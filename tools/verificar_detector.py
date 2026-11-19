"""Baixa/carrega o detector e verifica uma inferência vazia. Não mede qualidade."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
from src.automatic_pipeline import AutomaticPipeline,MODEL_NAME

def main():
    pipeline=AutomaticPipeline(None)
    print("Preparando modelo: " + MODEL_NAME, flush=True)
    pipeline.load()
    predictions=pipeline.detector.predict(np.zeros((640,640,3),dtype=np.uint8))
    print("Modelo carregado. Inferencia de verificacao retornou " + str(len(predictions)) + " deteccoes.")
    print("Isto nao valida a leitura nem o desempenho com placas reais.")
    import json
    import importlib.metadata
    import onnxruntime
    root=Path(__file__).resolve().parents[1]
    (root/"outputs").mkdir(exist_ok=True)
    (root/"outputs"/"detector_info.json").write_text(json.dumps({
        "model":MODEL_NAME,
        "open_image_models":importlib.metadata.version("open-image-models"),
        "onnxruntime":onnxruntime.__version__,
        "available_providers":onnxruntime.get_available_providers(),
        "source":"https://github.com/ankandrew/open-image-models",
        "check":"blank-image inference only, not accuracy validation"
    },indent=2),encoding="utf-8")

if __name__=="__main__":
    main()
