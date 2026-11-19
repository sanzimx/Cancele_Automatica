"""Tentativas adicionais somente em placas detectadas cujo OCR inicial falhou."""
from time import perf_counter
import cv2
import numpy as np

def retry_plate(reader,image,box,params,authorized):
    from src.vision import ALLOWLIST,normalize,valid_plate,select_candidate,map_box
    start=perf_counter()
    x0,y0,x1,y1=box
    plate=image[y0:y1,x0:x1]
    if plate.size==0:
        return None
    gray=cv2.cvtColor(plate,cv2.COLOR_BGR2GRAY)
    # Não usa o cadastro para transformar caracteres.
    regions=[("cinza_integral",gray,y0),
             ("cinza_sem_faixa_superior",gray[int(gray.shape[0]*.22):],y0+int(gray.shape[0]*.22))]
    cropped=regions[1][1]
    if cropped.size:
        contrast=cv2.createCLAHE(clipLimit=2.,tileGridSize=(4,4)).apply(cropped)
        soft=cv2.GaussianBlur(contrast,(0,0),1.)
        sharp=cv2.addWeighted(contrast,1.35,soft,-.35,0)
        regions.append(("contraste_nitidez",sharp,regions[1][2]))
    tokens=[]
    attempts=[]
    prepared=None
    for name,region,offset_y in regions:
        if region.size==0 or region.shape[0]<3:
            continue
        width=min(640,max(256,region.shape[1]*4))
        height=max(16,round(region.shape[0]*width/region.shape[1]))
        prepared=cv2.resize(region,(width,height),interpolation=cv2.INTER_CUBIC)
        mapping=(x0,offset_y,width/region.shape[1],height/region.shape[0])
        raw=reader.recognize(prepared,horizontal_list=[[0,width,0,height]],
                             free_list=[],allowlist=ALLOWLIST,detail=1,paragraph=False,
                             decoder="greedy",batch_size=1,workers=0)
        for bounds,text,score in raw:
            clean=normalize(text)
            token=dict(text=clean,confidence=float(score),
                       box=map_box(bounds,mapping,image.shape),method=name)
            tokens.append(token)
            attempts.append(dict(method=name,text=clean,confidence=float(score)))
    # Não junta tokens entre transformações diferentes.
    candidates=[t for t in tokens if t["confidence"]>=params.confidence and
                (valid_plate(t["text"]) if params.mode=="Veicular" else 3<=len(t["text"])<=10)]
    unique={t["text"] for t in candidates}
    if len(unique)>1:
        return dict(plate="",status="AMBIGUO",confidence=0.,tokens=tokens,
                    prepared=prepared,attempts=attempts,elapsed_ms=(perf_counter()-start)*1000)
    if not candidates:
        return dict(plate="",status="SEM_LEITURA",confidence=0.,tokens=tokens,
                    prepared=prepared,attempts=attempts,elapsed_ms=(perf_counter()-start)*1000)
    best=max(candidates,key=lambda t:t["confidence"])
    # Respeita o mesmo limite selecionado na interface.
    if best["confidence"]<params.confidence:
        return dict(plate="",status="SEM_LEITURA",confidence=0.,tokens=tokens,
                    prepared=prepared,attempts=attempts,elapsed_ms=(perf_counter()-start)*1000)
    allowed={normalize(t) for t in authorized}
    return dict(plate=best["text"],status="AUTORIZADO" if best["text"] in allowed else "NEGADO",
                confidence=best["confidence"],tokens=tokens,prepared=prepared,attempts=attempts,
                elapsed_ms=(perf_counter()-start)*1000)
