"""Fixtures sintéticas. Não simulam a distribuição de placas em ruas."""
from pathlib import Path
import csv
import cv2
import numpy as np
ROOT=Path(__file__).resolve().parents[1]/"data_samples"
ROOT.mkdir(exist_ok=True)
cases=[
 ("autorizada.png","ABC1D23","1","frontal","test"),
 ("negada.png","XYZ9A88","0","frontal","test"),
 ("antiga.png","ABC1234","0","frontal","test"),
 ("escura.png","ABC1D23","1","pouca_luz","test"),
 ("desfocada.png","XYZ9A88","0","desfoque","test"),
 ("sem_placa.png","","0","negativo","test")]
for name,text,_,condition,_ in cases:
    image=np.full((480,800,3),90,np.uint8)
    if text:
        cv2.rectangle(image,(170,190),(630,310),(245,245,245),-1)
        cv2.rectangle(image,(170,190),(630,310),(20,20,20),3)
        cv2.putText(image,text,(185,273),cv2.FONT_HERSHEY_SIMPLEX,2.5,(15,15,15),5)
    if condition=="pouca_luz":
        image=(image*.3).astype(np.uint8)
    if condition=="desfoque":
        image=cv2.GaussianBlur(image,(17,17),4)
    cv2.imencode(".png",image)[1].tofile(str(ROOT/name))
with (ROOT/"manifesto_sintetico.csv").open("w",newline="",encoding="utf-8") as f:
    writer=csv.writer(f)
    writer.writerow(["image","expected_plate","expected_authorized","condition","split"])
    writer.writerows(cases)
print("Seis amostras sintéticas geradas. Nenhuma métrica foi presumida.")
