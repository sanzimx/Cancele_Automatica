"""Manutenção do projeto: instalação, OCR e verificações com registros por etapa."""
import argparse
from datetime import datetime
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def execute(title,arguments,log):
    print("\n"+"="*66+"\n"+title+"\n"+"="*66,flush=True)
    started=time.monotonic()
    env=os.environ.copy()
    env["PYTHONUTF8"]="1"
    env["PYTHONUNBUFFERED"]="1"
    process=subprocess.Popen([sys.executable,*arguments],cwd=ROOT,env=env,
                             stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                             text=True,encoding="utf-8",errors="replace")
    with log.open("a",encoding="utf-8") as stream:
        stream.write("\n"+title+"\n")
        for line in process.stdout:
            print(line,end="",flush=True)
            stream.write(line)
        code=process.wait()
        stream.write(f"\nCodigo: {code}; tempo: {time.monotonic()-started:.2f} s\n")
    if code:
        raise RuntimeError(f"A etapa '{title}' falhou (codigo {code}). Registro: {log}")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=["instalar","ocr","validar"])
    args=parser.parse_args()
    if sys.version_info[:2]!=(3,11):
        raise RuntimeError("Execute com o Python 3.11 do ambiente .venv.")
    outputs=ROOT/"outputs"
    outputs.mkdir(exist_ok=True)
    log=outputs/(args.action+"_"+datetime.now().strftime("%Y%m%d_%H%M%S")+".log")
    print("Pasta do projeto:",ROOT)
    print("Registro:",log)
    if args.action in ("instalar","ocr"):
        # requirements.txt já inclui os dois reconhecedores e o detector.
        execute("Instalando dependencias do projeto",["-m","pip","install","-r","requirements.txt"],log)
        execute("Conferindo dependencias",["-m","pip","check"],log)
        execute("Preparando detector de placas",["tools/verificar_detector.py"],log)
        execute("Preparando e ativando OCR especializado",["tools/ativar_ocr_especializado.py"],log)
    execute("Conferindo sintaxe Python",
            ["-m","compileall","-q","app.py","evaluate.py","ocr_service.py","src","tests","tools"],log)
    execute("Executando testes de regras",["-m","unittest","discover","-s","tests","-v"],log)
    if args.action=="instalar":
        if not (ROOT/"data_samples"/"manifesto_sintetico.csv").exists():
            execute("Gerando imagens sinteticas de demonstracao",["tools/gerar_amostras.py"],log)
        if not (ROOT/"docs"/"APRESENTACAO.pdf").exists():
            execute("Gerando apresentacao PDF",["tools/gerar_apresentacao_pdf.py"],log)
    execute("Verificando consistencia do ambiente",["-m","pip","check"],log)
    freeze=subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,
                          text=True,encoding="utf-8",errors="replace",check=True)
    (outputs/"ambiente_instalado.txt").write_text(freeze.stdout,encoding="utf-8")
    execute("Organizando arquivos antigos e registrando inventario",["tools/organizar_projeto.py"],log)
    (outputs/"ultima_verificacao.json").write_text(json.dumps({
        "date":datetime.now().isoformat(timespec="seconds"),
        "action":args.action,"python":sys.version,"log":str(log),
        "checks":"dependencies, syntax, unit tests",
        "hardware_validated":False,"ocr_accuracy_validated":False
    },indent=2),encoding="utf-8")
    print("\nConcluido. Para abrir o programa, execute iniciar.bat.")
    print("As verificacoes nao substituem os testes com fotos, camera e circuito.")
    return 0

if __name__=="__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print("\nFALHA:",error,flush=True)
        raise SystemExit(1)
