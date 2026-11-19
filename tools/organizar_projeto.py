"""Arquiva somente sobras conhecidas e produz inventário sem apagar arquivos."""
from datetime import datetime
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
ARCHIVE=ROOT/"arquivo"
SKIP={".git",".venv","__pycache__",".agents",".codex",".aws"}
KNOWN_BATCHES=("INSTALAR_CORRIGIDO.bat","ATIVAR_DETECTOR.bat",
               "ATIVAR_OCR_DE_PLACAS.bat","BAIXAR_FOTO_REAL.bat")
KNOWN_SUPPORT=("tmp_transfer","save_helpers","Cancela_Inteligente_Entrega.tar")

def inside(path,base):
    return path.resolve().is_relative_to(base.resolve())

def archive_path(source,category):
    # Verificação explícita antes de qualquer movimentação, inclusive de diretórios.
    if source.is_symlink() or not inside(source,PROJECT):
        raise ValueError("Origem fora da pasta autorizada ou link: "+str(source))
    target=ARCHIVE/category/source.name
    if not inside(target,ROOT):
        raise ValueError("Destino fora do projeto.")
    if not source.exists():
        return None
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():
        target=target.with_name(target.stem+"_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f")+target.suffix)
    source.rename(target)
    return {"from":str(source),"to":str(target)}

def inspect(folder):
    rows=[]
    def visit(path):
        try:
            children=sorted(path.iterdir(),key=lambda p:p.name.lower())
        except OSError as error:
            rows.append({"path":str(path.relative_to(PROJECT)),"type":"unreadable",
                         "reason":type(error).__name__})
            return
        for child in children:
            rel=str(child.relative_to(PROJECT))
            if child.name in SKIP or child.name.startswith("."):
                continue
            if child.is_symlink():
                rows.append({"path":rel,"type":"link_preserved"})
            elif child.is_dir():
                rows.append({"path":rel,"type":"directory"})
                # Arquivo, resultados e modelos aparecem no inventário, sem percorrer dados pesados.
                if child.name not in {"arquivo","outputs","models"}:
                    visit(child)
            else:
                try:
                    rows.append({"path":rel,"type":"file","bytes":child.stat().st_size})
                except OSError:
                    rows.append({"path":rel,"type":"file_unreadable"})
    visit(folder)
    return rows

def main():
    moved=[]
    for name in KNOWN_BATCHES:
        result=archive_path(ROOT/name,"lotes_antigos")
        if result:
            moved.append(result)
    for name in KNOWN_SUPPORT:
        result=archive_path(PROJECT/name,"apoio_da_preparacao")
        if result:
            moved.append(result)
    legacy=ROOT/"ocr_worker.py"
    if legacy.exists():
        # O fluxo ativo usa ocr_service.py. Só arquiva quando não existe chamada ativa.
        references=[]
        for path in [ROOT/"app.py",ROOT/"src"/"vision.py",ROOT/"src"/"persistent_ocr.py"]:
            if path.exists() and "ocr_worker.py" in path.read_text(encoding="utf-8"):
                references.append(str(path))
        if not references:
            result=archive_path(legacy,"codigo_antigo")
            if result:
                moved.append(result)
    report=ROOT/"docs"/"organizacao"
    report.mkdir(parents=True,exist_ok=True)
    inventory=inspect(PROJECT)
    stamp=datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    payload={"timestamp":datetime.now().isoformat(timespec="seconds"),
             "moved":moved,"inventory":inventory,
             "policy":"No deletions. Unknown files and user data are preserved."}
    (report/"INVENTARIO_ATUAL.json").write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
    if moved:
        (report/("movimentacoes_"+stamp+".json")).write_text(json.dumps(moved,ensure_ascii=False,indent=2),encoding="utf-8")
    lines=["# Inventario local do Projeto de Pedro","",
           "Data: "+payload["timestamp"],"",
           "Nenhum arquivo foi apagado. Itens desconhecidos foram preservados.",
           "Ambiente virtual, dados de resultados e modelos nao foram percorridos.","",
           "## Movimentacoes desta execucao",""]
    lines.extend("- "+m["from"]+" -> "+m["to"] for m in moved)
    if not moved:
        lines.append("Nenhum arquivo antigo conhecido precisou ser movido.")
    lines.extend(["","## Arquivos e pastas encontrados",""])
    lines.extend("- "+r["path"]+" ("+r["type"]+")" for r in inventory)
    (report/"INVENTARIO_ATUAL.md").write_text("\n".join(lines),encoding="utf-8")
    print("Organizacao concluida. Inventario em docs/organizacao/INVENTARIO_ATUAL.md")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
