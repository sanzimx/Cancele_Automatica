"""Pipeline local. OCR detecta texto; candidatos são hipóteses, não detecção treinada de placas."""
from dataclasses import dataclass
from itertools import combinations
from time import perf_counter
import re
import cv2
import numpy as np

ALLOWLIST = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
PATTERN = re.compile(r"(?:[A-Z]{3}[0-9]{4}|[A-Z]{3}[0-9][A-Z][0-9]{2})")

def normalize(text):
    return re.sub(r"[^A-Z0-9]", "", str(text).upper())

def valid_plate(text):
    return PATTERN.fullmatch(normalize(text)) is not None

@dataclass(frozen=True)
class Params:
    confidence: float = 0.60
    width: int = 640
    clip: float = 2.0
    # Frações da imagem original: esquerda, topo, direita, base
    roi: tuple = (0.0, 0.0, 1.0, 1.0)
    mode: str = "Veicular"
    mask_osd: bool = False
    auto_detect: bool = True
    detector_confidence: float = 0.35
    detector_detail: bool = False

def roi_pixels(shape, roi):
    h, w = shape[:2]
    a, b, c, d = map(float, roi)
    if not (0 <= a < c <= 1 and 0 <= b < d <= 1):
        raise ValueError("Região inválida: início deve ser menor que o fim, entre 0 e 100%.")
    return int(a*w), int(b*h), max(int(c*w), 1), max(int(d*h), 1)

def preprocess(image, params):
    if image is None or image.ndim != 3 or image.size == 0:
        raise ValueError("Imagem vazia ou incompatível.")
    if not 0 <= params.confidence <= 1 or not 320 <= params.width <= 2560:
        raise ValueError("Confiança ou largura fora dos limites.")
    x0, y0, x1, y1 = roi_pixels(image.shape, params.roi)
    crop = image[y0:y1, x0:x1].copy()
    if crop.size == 0:
        raise ValueError("Região menor que um pixel.")
    # Máscara opcional reproduz a posição do OSD da câmera original.
    if params.mask_osd:
        h, w = image.shape[:2]
        for ax, ay, bx, by in [(0, 0, .30, .11), (.65, .82, 1, 1)]:
            left, top = max(x0, int(ax*w)), max(y0, int(ay*h))
            right, bottom = min(x1, int(bx*w)), min(y1, int(by*h))
            if right > left and bottom > top:
                crop[top-y0:bottom-y0, left-x0:right-x0] = 0
    scale = params.width / crop.shape[1]
    resized = cv2.resize(crop, (params.width, max(1, round(crop.shape[0]*scale))),
                         interpolation=cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    contrast = cv2.createCLAHE(clipLimit=max(.1, params.clip), tileGridSize=(8, 8)).apply(gray)
    prepared = cv2.bilateralFilter(contrast, 5, 35, 35)
    # Largura/altura arredondadas exigem escalas independentes.
    mapping = (x0, y0, resized.shape[1]/crop.shape[1], resized.shape[0]/crop.shape[0])
    return prepared, mapping

def map_box(box, mapping, shape):
    x0, y0, sx, sy = mapping
    h, w = shape[:2]
    return [[max(0, min(w-1, round(float(x)/sx+x0))),
             max(0, min(h-1, round(float(y)/sy+y0)))] for x, y in box]

def bounds(token):
    xs, ys = zip(*token["box"])
    return min(xs), min(ys), max(xs), max(ys)

def merge_tokens(tokens):
    """Junta no máximo dois blocos próximos, na mesma linha ou em duas linhas."""
    candidates = list(tokens)
    for first, second in combinations(tokens, 2):
        a, b = bounds(first), bounds(second)
        ha, hb = max(1, a[3]-a[1]), max(1, b[3]-b[1])
        height = max(ha, hb)
        same_line = abs((a[1]+a[3]-b[1]-b[3])/2) < .5*height
        gap = max(a[0], b[0])-min(a[2], b[2])
        stacked = (not same_line and abs((a[0]+a[2]-b[0]-b[2])/2) <
                   .5*max(a[2]-a[0], b[2]-b[0]) and
                   0 <= max(a[1], b[1])-min(a[3], b[3]) < .8*height)
        if same_line and -.2*height <= gap <= 1.5*height:
            ordered = sorted([first, second], key=lambda t: bounds(t)[0])
        elif stacked:
            ordered = sorted([first, second], key=lambda t: bounds(t)[1])
        else:
            continue
        left, top = min(a[0], b[0]), min(a[1], b[1])
        right, bottom = max(a[2], b[2]), max(a[3], b[3])
        candidates.append(dict(text="".join(t["text"] for t in ordered),
                               confidence=min(t["confidence"] for t in ordered),
                               box=[[left,top],[right,top],[right,bottom],[left,bottom]]))
    return candidates

def select_candidate(tokens, authorized, params):
    allowed = {normalize(t) for t in authorized if normalize(t)}
    qualified = [t for t in tokens if t["confidence"] >= params.confidence]
    candidates = merge_tokens(qualified)
    if params.mode == "Veicular":
        candidates = [t for t in candidates if valid_plate(t["text"])]
    else:
        candidates = [t for t in candidates if 3 <= len(t["text"]) <= 10]
    # A lista de autorização não influencia a escolha da leitura.
    candidates.sort(key=lambda t: t["confidence"], reverse=True)
    unique = {}
    for token in candidates:
        unique.setdefault(token["text"], token)
    if not unique:
        return None, "SEM_LEITURA"
    # Duas placas plausíveis na mesma região exigem reposicionamento.
    if len(unique) > 1:
        return None, "AMBIGUO"
    chosen = next(iter(unique.values()))
    return chosen, "AUTORIZADO" if chosen["text"] in allowed else "NEGADO"

class LocalEngine:
    def __init__(self):
        self.reader = None

    def load(self):
        if self.reader is None:
            import easyocr
            # O modo quantizado causou 0xc000001d na LSTM do PyTorch
            # neste computador. Usar o modelo sem quantização.
            self.reader = easyocr.Reader(["en"], gpu=False, quantize=False)

    def analyze(self, image, params, authorized):
        self.load()  # download/aquecimento ficam fora do tempo da pipeline
        if params.auto_detect:
            from src.automatic_pipeline import AutomaticPipeline
            if not hasattr(self, "automatic_pipeline"):
                self.automatic_pipeline = AutomaticPipeline(self,use_specialized=True)
            return self.automatic_pipeline.analyze(image, params, authorized)
        start = perf_counter()
        prepared, mapping = preprocess(image, params)
        raw = self.reader.readtext(prepared, allowlist=ALLOWLIST, detail=1, paragraph=False,
                                   decoder="greedy", workers=0, batch_size=1,
                                   canvas_size=params.width, mag_ratio=1.0)
        tokens = []
        for box, text, confidence in raw:
            tokens.append(dict(text=normalize(text), confidence=float(confidence),
                               box=map_box(box, mapping, image.shape)))
        chosen, status = select_candidate(tokens, authorized, params)
        elapsed_ms = (perf_counter()-start)*1000
        overlay = image.copy()
        x0,y0,x1,y1 = roi_pixels(image.shape, params.roi)
        cv2.rectangle(overlay, (x0,y0), (x1-1,y1-1), (255,180,0), 2)
        for token in tokens:
            cv2.polylines(overlay, [np.array(token["box"], np.int32)], True, (150,150,150), 1)
        if chosen:
            color = (0,190,0) if status == "AUTORIZADO" else (0,0,230)
            cv2.polylines(overlay, [np.array(chosen["box"], np.int32)], True, color, 3)
            a,b,_,_ = bounds(chosen)
            cv2.putText(overlay, chosen["text"], (a,max(22,b-8)),
                        cv2.FONT_HERSHEY_SIMPLEX, .8, color, 2)
        cv2.putText(overlay, status, (20,35), cv2.FONT_HERSHEY_SIMPLEX,
                    .8, (0,190,0) if status=="AUTORIZADO" else (0,0,230), 2)
        return dict(plate=chosen["text"] if chosen else "",
                    confidence=chosen["confidence"] if chosen else 0.0,
                    status=status, elapsed_ms=elapsed_ms, tokens=tokens,
                    prepared=prepared, overlay=overlay)


# A interface e o avaliador passam a reutilizar um trabalhador isolado.
from src.persistent_ocr import Engine
