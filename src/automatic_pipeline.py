"""Detecção de várias placas e OCR por recortes da imagem original."""
from dataclasses import replace
from time import perf_counter
import cv2
import numpy as np

MODEL_NAME="yolo-v9-t-640-license-plate-end2end"

def iou(a,b):
    x0,y0=max(a[0],b[0]),max(a[1],b[1])
    x1,y1=min(a[2],b[2]),min(a[3],b[3])
    inter=max(0,x1-x0)*max(0,y1-y0)
    union=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter
    return inter/union if union>0 else 0.

def suppress_duplicates(boxes,threshold=.35):
    kept=[]
    for box in sorted(boxes,key=lambda b:b["confidence"],reverse=True):
        if all(iou(box["box"],previous["box"])<threshold for previous in kept):
            kept.append(box)
    return kept

def aggregate_status(plates,total_detections):
    # Nunca escolhe o autorizado entre vários veículos.
    if total_detections==0:
        return "SEM_PLACA"
    if total_detections>1:
        return "MULTIPLAS_PLACAS"
    return plates[0]["status"] if plates else "SEM_LEITURA"

def expanded_crop(box,shape,margin=.12):
    h,w=shape[:2]
    x0,y0,x1,y1=box
    dx=max(2,round((x1-x0)*margin))
    dy=max(2,round((y1-y0)*margin))
    return max(0,x0-dx),max(0,y0-dy),min(w,x1+dx),min(h,y1+dy)

class AutomaticPipeline:
    def __init__(self,ocr,use_specialized=False):
        self.ocr=ocr
        self.detector=None
        self.specialized=None
        if use_specialized:
            from pathlib import Path
            import json
            flag=Path(__file__).resolve().parents[1]/"ocr_especializado.json"
            if flag.exists() and json.loads(flag.read_text(encoding="utf-8")).get("enabled"):
                from src.specialized_ocr import SpecializedOCR
                self.specialized=SpecializedOCR()

    def load(self):
        if self.detector is None:
            try:
                from open_image_models import create_detector
            except ImportError as error:
                raise RuntimeError("Detector não instalado. Feche o programa e execute ATIVAR_DETECTOR.bat.") from error
            self.detector=create_detector(MODEL_NAME)
        if self.specialized is not None:
            self.specialized.load()

    def detect(self,image,params):
        from src.vision import roi_pixels
        x0,y0,x1,y1=roi_pixels(image.shape,params.roi)
        windows=[(x0,y0,x1,y1)]
        # Janelas sobrepostas preservam placas pequenas ao reduzir a cena para o modelo.
        if params.detector_detail:
            w,h=x1-x0,y1-y0
            tw,th=max(1,round(w*.62)),max(1,round(h*.62))
            windows.extend([(a,b,a+tw,b+th) for a in (x0,x1-tw) for b in (y0,y1-th)])
        boxes=[]
        for left,top,right,bottom in windows:
            crop=image[top:bottom,left:right]
            for detection in self.detector.predict(crop):
                score=float(detection.confidence)
                if score<params.detector_confidence:
                    continue
                box=detection.bounding_box
                a=max(left,min(right,int(box.x1)+left))
                b=max(top,min(bottom,int(box.y1)+top))
                c=max(left,min(right,int(box.x2)+left))
                d=max(top,min(bottom,int(box.y2)+top))
                if c-a>=10 and d-b>=5:
                    boxes.append(dict(box=[a,b,c,d],confidence=score))
        return suppress_duplicates(boxes)

    def analyze(self,image,params,authorized):
        from src.vision import preprocess,roi_pixels
        self.load()  # download/inicialização separados da latência de inferência
        start=perf_counter()
        detections=self.detect(image,params)
        detection_ms=(perf_counter()-start)*1000
        overlay=image.copy()
        h,w=image.shape[:2]
        x0,y0,x1,y1=roi_pixels(image.shape,params.roi)
        cv2.rectangle(overlay,(x0,y0),(x1-1,y1-1),(255,180,0),2)
        plates=[]
        tokens=[]
        previews=[]
        # Limite explícito de trabalho por pedido para não bloquear a bancada.
        for index,detection in enumerate(detections[:8],1):
            crop=expanded_crop(detection["box"],image.shape)
            a,b,c,d=crop
            local=replace(params,auto_detect=False,roi=(a/w,b/h,c/w,d/h))
            result=self.ocr.analyze(image,local,authorized)
            if result["status"]=="SEM_LEITURA" and self.specialized is not None:
                extra=self.specialized.analyze(image,detection["box"],params,authorized)
                result["tokens"].extend(extra["tokens"])
                result["elapsed_ms"]+=extra["elapsed_ms"]
                result["review_candidates"]=extra.get("review_candidates",[])
                result["review_error"]=extra.get("review_error", "")
                if extra["status"] in ("AUTORIZADO","NEGADO"):
                    result.update(plate=extra["plate"],status=extra["status"],
                                  confidence=extra["confidence"],prepared=extra["prepared"],
                                  recognizer_model=extra["recognizer_model"])
            retry_attempts=[]
            if result["status"] == "SEM_LEITURA" and hasattr(self.ocr,"reader"):
                from src.plate_retry import retry_plate
                retry=retry_plate(self.ocr.reader,image,detection["box"],params,authorized)
                if retry:
                    result["elapsed_ms"]+=retry["elapsed_ms"]
                    result["tokens"].extend(retry["tokens"])
                    retry_attempts=retry["attempts"]
                    if retry["status"] in ("AUTORIZADO","NEGADO","AMBIGUO"):
                        result.update(plate=retry["plate"],status=retry["status"],
                                      confidence=retry["confidence"],prepared=retry["prepared"])
            from src.reading_review import raw_diagnostic
            diagnostic=raw_diagnostic(result["tokens"],params.confidence,params.mode)
            if not result["plate"] and result["status"]=="SEM_LEITURA" and diagnostic["raw_text"]:
                result["status"]=diagnostic["rejection_reason"]
            entry=dict(index=index,plate=result["plate"],status=result["status"],
                       confidence=result["confidence"],box=detection["box"],
                       crop_box=list(crop),detector_confidence=detection["confidence"],
                       elapsed_ms=result["elapsed_ms"],retry_attempts=retry_attempts,
                       original_plate_width=detection["box"][2]-detection["box"][0],
                       original_plate_height=detection["box"][3]-detection["box"][1],
                       recognizer_model=result.get("recognizer_model","easyocr"),
                       review_candidates=result.get("review_candidates",[]),
                       review_error=result.get("review_error",""),**diagnostic)
            plates.append(entry)
            tokens.extend(dict(t,plate_index=index) for t in result["tokens"])
            prepared=result["prepared"]
            factor=min(640/prepared.shape[1],180/prepared.shape[0])
            previews.append(cv2.resize(prepared,(max(1,round(prepared.shape[1]*factor)),
                                                max(1,round(prepared.shape[0]*factor)))))
            color=(0,190,0) if result["status"]=="AUTORIZADO" else (0,165,255)
            a,b,c,d=detection["box"]
            cv2.rectangle(overlay,(a,b),(c,d),color,3)
            label=f'#{index} {result["plate"] or diagnostic["raw_text"] or result["status"]}'
            cv2.putText(overlay,label,(a,max(20,b-7)),cv2.FONT_HERSHEY_SIMPLEX,.65,color,2)
        # Mostrar também detecções acima do limite de OCR.
        for detection in detections[8:]:
            a,b,c,d=detection["box"]
            cv2.rectangle(overlay,(a,b),(c,d),(150,150,150),2)
        if previews:
            montage=np.full((sum(p.shape[0]+8 for p in previews),640),235,np.uint8)
            y=0
            for preview in previews:
                montage[y:y+preview.shape[0],:preview.shape[1]]=preview
                y+=preview.shape[0]+8
        else:
            montage,_=preprocess(image,replace(params,auto_detect=False))
        status=aggregate_status(plates,len(detections))
        single=plates[0] if len(detections)==1 and plates else None
        cv2.putText(overlay,status,(20,35),cv2.FONT_HERSHEY_SIMPLEX,.8,
                    (0,190,0) if status=="AUTORIZADO" else (0,0,230),2)
        return dict(plate=single["plate"] if single else "",
                    raw_text=single["raw_text"] if single else "",
                    raw_confidence=single["raw_confidence"] if single else 0.,
                    rejection_reason=single["rejection_reason"] if single else "",
                    review_candidates=single["review_candidates"] if single else [],
                    confidence=single["confidence"] if single else 0.,
                    status=status,elapsed_ms=(perf_counter()-start)*1000,
                    detection_ms=detection_ms,detector_model=MODEL_NAME,
                    detections=detections,detected_count=len(detections),
                    skipped_count=max(0,len(detections)-8),plates=plates,
                    tokens=tokens,prepared=montage,overlay=overlay)
