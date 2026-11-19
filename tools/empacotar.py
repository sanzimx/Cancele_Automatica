"""Cria pacote para instalação limpa, sem ambiente virtual, cadastros ou histórico."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import os
ROOT=Path(__file__).resolve().parents[1]
ROOT_FILES={
    "app.py","evaluate.py","ocr_service.py","requirements.txt",".gitignore",
    "README.md","LEIA_PRIMEIRO.txt","COMECE_AQUI.html",
    "instalar.bat","iniciar.bat","ativar_ocr.bat","validar.bat","gerar_pacote.bat"
}
DIRECTORIES={"src","tools","tests","docs","firmware","assets"}
SKIP={".git",".venv","__pycache__","outputs","dist","models","arquivo",
      "organizacao","Fotos_Cancela","reais","evidencias_reais"}
SAMPLES={"LEIA_ME.md","placa_demo.pgm","manifesto_incluido.csv",
         "manifesto_sintetico.csv","autorizada.png","negada.png",
         "antiga.png","escura.png","desfocada.png","sem_placa.png"}

def include(path):
    rel=path.relative_to(ROOT)
    if any(part in SKIP or part.startswith(".env") for part in rel.parts):
        return False
    if path.is_symlink() or path.suffix in {".pyc",".log"}:
        return False
    if len(rel.parts)==1:
        return path.name in ROOT_FILES
    if rel.parts[0]=="data_samples":
        return len(rel.parts)==2 and path.name in SAMPLES
    return rel.parts[0] in DIRECTORIES

def main():
    output=ROOT/"dist"
    output.mkdir(exist_ok=True)
    target=output/"Cancela_Inteligente_Instalacao.zip"
    paths=[]
    for base,directories,files in os.walk(ROOT,followlinks=False):
        base=Path(base)
        directories[:]=[name for name in directories if name not in SKIP and
                        not name.startswith(".") and not (base/name).is_symlink()]
        if base==ROOT:
            directories[:]=[name for name in directories if name in DIRECTORIES or name=="data_samples"]
        for name in files:
            path=base/name
            if include(path):
                paths.append(path)
    paths.sort()
    missing=[name for name in ROOT_FILES if not (ROOT/name).exists()]
    if missing:
        raise RuntimeError("Arquivos necessários ausentes: "+", ".join(sorted(missing)))
    with ZipFile(target,"w",ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path,Path("cancela_final")/path.relative_to(ROOT))
    with ZipFile(target) as archive:
        bad=archive.testzip()
        if bad:
            raise RuntimeError("Falha na verificação do ZIP: "+bad)
    print("Pacote criado:",target)
    print("Arquivos:",len(paths))
    print("O destinatário deve extrair e executar instalar.bat com internet.")
    print("A instalação numa máquina nova ainda precisa de teste real.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
