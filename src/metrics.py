"""Métricas calculadas a partir de casos rotulados. Sem valores inventados."""
from statistics import mean
from math import ceil

def distance(a,b):
    row = list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        nxt = [i]
        for j,cb in enumerate(b,1):
            nxt.append(min(nxt[-1]+1,row[j]+1,row[j-1]+(ca!=cb)))
        row = nxt
    return row[-1]

def summarize(rows):
    if not rows:
        raise ValueError("Nenhum caso avaliado.")
    positive = [r for r in rows if r["expected_plate"]]
    negative = [r for r in rows if not r["expected_plate"]]
    times = sorted(float(r["elapsed_ms"]) for r in rows)
    expected_chars = sum(len(r["expected_plate"]) for r in positive)
    errors = sum(distance(r["expected_plate"],r["predicted_plate"]) for r in positive)
    total = len(rows)
    return {
        "cases":total,
        "execution_errors":sum(bool(r.get("error")) for r in rows),
        "exact_match_all":sum(r["expected_plate"]==r["predicted_plate"] and
                              not r.get("error") for r in rows)/total,
        "exact_match_positive":(sum(r["expected_plate"]==r["predicted_plate"] and
                                    not r.get("error") for r in positive)/len(positive)
                                if positive else None),
        "character_error_rate_positive":errors/expected_chars if expected_chars else None,
        "false_read_rate_negative":(sum(bool(r["predicted_plate"]) for r in negative)/len(negative)
                                    if negative else None),
        "decision_accuracy":sum(r["expected_authorized"]==r["predicted_authorized"] and
                                not r.get("error") for r in rows)/total,
        "false_authorizations":sum(not r["expected_authorized"] and
                                   r["predicted_authorized"] for r in rows),
        "mean_pipeline_ms":mean(times),
        "p95_pipeline_ms":times[max(0,ceil(.95*len(times))-1)],
        "timing_scope":"preprocessing + OCR + decision, excluding load/capture/render",
    }
