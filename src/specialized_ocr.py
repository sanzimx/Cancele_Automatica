"""OCR de placas opcional, executado no recorte original sem realce de nitidez."""
from pathlib import Path
from time import perf_counter
import tempfile
import cv2
import numpy as np

MODEL="cct-s-v2-global-model"

def interpret(prediction,minimum,authorized,mode="Veicular"):
    from src.vision import normalize,valid_plate
    raw=str(prediction.plate).upper()
    text=normalize(raw)
    probabilities=np.asarray(prediction.char_probs,dtype=float).reshape(-1)
    # O vetor pode incluir posições de padding. Não atribuir escore inventado.
    if probabilities.size < len(raw):
        raise ValueError("Escores por caractere não correspondem ao texto retornado.")
    positions=[i for i,c in enumerate(raw) if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"]
    values=[float(probabilities[i]) for i in positions]
    score=min(values) if values else 0.
    if any(not np.isfinite(v) or not 0<=v<=1 for v in values):
        raise ValueError("Escores inválidos do OCR de placas.")
    format_ok=valid_plate(text) if mode=="Veicular" else 3<=len(text)<=10
    if not format_ok or score<minimum:
        return "",score,"SEM_LEITURA"
    return text,score,"AUTORIZADO" if text in {normalize(x) for x in authorized} else "NEGADO"

class SpecializedOCR:
    def __init__(self):
        self.model=None
    def load(self):
        if self.model is None:
            from fast_plate_ocr import LicensePlateRecognizer
            self.model=LicensePlateRecognizer(MODEL,device="cpu")
            from src.reading_review import RecordingSession
            self.model.model=RecordingSession(self.model.model)
    def analyze(self,image,box,params,authorized):
        self.load()
        start=perf_counter()
        a,b,c,d=box
        plate=image[b:d,a:c].copy()
        if plate.size==0:
            raise ValueError("Recorte vazio para OCR de placas.")
        # Caminho de arquivo permite que a biblioteca aplique o modo de cor correto.
        with tempfile.TemporaryDirectory(prefix="placa_especializada_") as folder:
            path=Path(folder)/"placa.png"
            ok,encoded=cv2.imencode(".png",plate)
            if not ok:
                raise ValueError("Falha ao preparar recorte.")
            encoded.tofile(str(path))
            prediction=self.model.run(str(path),return_confidence=True)[0]
        text,score,status=interpret(prediction,params.confidence,authorized,params.mode)
        review_candidates=[]
        review_error=""
        if not text and params.mode=="Veicular":
            try:
                from src.reading_review import constrained_candidates
                config=self.model.config
                output=self.model.model.outputs[self.model.plate_output_name]
                review_candidates=constrained_candidates(output,config.alphabet,
                                                          config.max_plate_slots,config.pad_char)
            except (ValueError,KeyError,AttributeError) as error:
                review_error=str(error)
        token=dict(text=str(prediction.plate),confidence=score,
                   box=[[a,b],[c,b],[c,d],[a,d]],method="fast_plate_ocr")
        return dict(plate=text,status=status,confidence=score,tokens=[token],
                    prepared=cv2.cvtColor(plate,cv2.COLOR_BGR2GRAY),
                    elapsed_ms=(perf_counter()-start)*1000,
                    recognizer_model=MODEL,review_candidates=review_candidates,
                    review_error=review_error)
