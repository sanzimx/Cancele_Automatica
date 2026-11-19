"""Avaliação offline reproduzível. Não abre porta serial."""
import argparse
import csv
import json
from datetime import datetime
from pathlib import Path
from dataclasses import asdict
from src.vision import Engine, Params, normalize, valid_plate
from src.metrics import summarize

ROOT=Path(__file__).resolve().parent

def run_evaluation(manifest,params,authorized,engine=None):
    from app import load_image
    manifest=Path(manifest).resolve()
    engine=engine or Engine()
    with manifest.open(encoding="utf-8-sig",newline="") as f:
        cases=list(csv.DictReader(f))
    if not cases:
        raise ValueError("Manifesto vazio.")
    required={"image","expected_plate","expected_authorized","condition","split"}
    if not required.issubset(cases[0]):
        raise ValueError("CSV exige colunas: "+", ".join(sorted(required)))
    engine.load()
    output=ROOT/"outputs"/("avaliacao_"+datetime.now().strftime("%Y%m%d_%H%M%S_%f"))
    output.mkdir(parents=True)
    rows=[]
    allowed={normalize(x) for x in authorized}
    for index,case in enumerate(cases,1):
        expected=normalize(case["expected_plate"])
        expected_auth=case["expected_authorized"].strip()
        if expected_auth not in ("0","1"):
            raise ValueError("expected_authorized deve ser 0 ou 1.")
        if params.mode=="Veicular" and expected and not valid_plate(expected):
            raise ValueError("Rótulo veicular inválido: "+expected)
        if (expected_auth=="1") != (bool(expected) and expected in allowed):
            raise ValueError("Rótulo de autorização não corresponde ao cadastro: "+expected)
        path=(manifest.parent/case["image"]).resolve()
        if not path.is_relative_to(manifest.parent):
            raise ValueError("Caminho deve permanecer na pasta do conjunto.")
        row=dict(case_id=index,image=case["image"],condition=case["condition"],
                 split=case["split"],expected_plate=expected,
                 expected_authorized=expected_auth=="1",predicted_plate="",
                 predicted_authorized=False,elapsed_ms=0.0,error="")
        try:
            result=engine.analyze(load_image(path),params,allowed)
            row.update(predicted_plate=result["plate"],
                       predicted_authorized=result["status"]=="AUTORIZADO",
                       elapsed_ms=result["elapsed_ms"])
            import cv2
            cv2.imencode(".png",result["overlay"])[1].tofile(str(output/f"caso_{index:03}.png"))
        except Exception as error:
            row["error"]=type(error).__name__
        rows.append(row)
    metrics=summarize(rows)
    groups={}
    for key in ("condition","split"):
        groups[key]={value:summarize([r for r in rows if r[key]==value])
                     for value in sorted({r[key] for r in rows})}
    payload=dict(metrics=metrics,groups=groups,params=asdict(params),
                 authorized=sorted(allowed),manifest=str(manifest),rows=rows)
    (output/"metricas.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    with (output/"resultados.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    lines=["# Resultados medidos", "",f"Conjunto: {manifest.name}",
           f"Casos: {metrics['cases']}",f"Erros de execução: {metrics['execution_errors']}",
           f"Acerto exato total: {metrics['exact_match_all']:.1%}",
           f"Acerto da decisão: {metrics['decision_accuracy']:.1%}",
           f"Autorizações falsas: {metrics['false_authorizations']}",
           f"Tempo médio da pipeline: {metrics['mean_pipeline_ms']:.1f} ms",
           f"P95: {metrics['p95_pipeline_ms']:.1f} ms","",
           "Tempo exclui download/aquecimento dos pesos, captura e comunicação serial.",
           "Casos sintéticos não representam desempenho em cenas reais.",
           "Erros de execução contam como falha de qualidade. Tempo zero desses erros afeta a média.",
           "Não compare ajustes feitos sobre o conjunto de teste como resultados independentes."]
    (output/"RELATORIO.md").write_text("\n".join(lines),encoding="utf-8")
    return output

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("--config",default="config.local.json")
    args=parser.parse_args()
    config=json.loads(Path(args.config).read_text(encoding="utf-8"))
    print(run_evaluation(Path(args.manifest),Params(**config["params"]),config["authorized"]))
