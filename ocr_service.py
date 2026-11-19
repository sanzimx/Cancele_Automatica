"""Serviço OCR por stdin/stdout. Carrega modelos uma vez por sessão."""
import os
# Quantização permanece desativada no LocalEngine.
THREADS=max(1,min(4,(os.cpu_count() or 2)//2))
os.environ["OMP_NUM_THREADS"]=str(THREADS)
os.environ["MKL_NUM_THREADS"]=str(THREADS)
import contextlib
import json
from pathlib import Path
import sys
import traceback
import numpy as np
from src.vision import LocalEngine,Params

def send(message):
    print(json.dumps(message),flush=True)

def main():
    with contextlib.redirect_stdout(sys.stderr):
        import torch
        torch.set_num_threads(THREADS)
        engine=LocalEngine()
        print("OCR persistente: CPU, quantize=False, threads="+str(THREADS),flush=True)
        engine.load()
    send({"type":"ready"})
    for line in sys.stdin:
        try:
            request=json.loads(line)
            work=Path(request["folder"])
            config=json.loads((work/"config.json").read_text(encoding="utf-8"))
            image=np.load(work/"entrada.npy",allow_pickle=False)
            with contextlib.redirect_stdout(sys.stderr):
                result=engine.analyze(image,Params(**config["params"]),config["authorized"])
            # Sem compressão: evita gastar CPU compactando resultados temporários.
            np.savez(work/"imagens.npz",prepared=result.pop("prepared"),
                     overlay=result.pop("overlay"))
            (work/"resultado.json").write_text(json.dumps(result),encoding="utf-8")
            send({"type":"result","id":request["id"]})
        except Exception as error:
            traceback.print_exc(file=sys.stderr)
            send({"type":"error", "message":str(error)})
if __name__=="__main__":
    main()
