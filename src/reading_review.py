"""Hipóteses gerais por formato, baseadas nas saídas completas do modelo."""
import math
import numpy as np

LETTERS="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
DIGITS="0123456789"
PATTERNS=("LLLDDDD","LLLDLDD")

def constrained_candidates(output,alphabet,slots,pad_char,limit=3):
    """Não altera escores por caractere nem consulta placas autorizadas."""
    alphabet=list(alphabet)
    values=np.asarray(output,dtype=float)
    if values.size!=slots*len(alphabet) or slots<7 or len(set(alphabet))!=len(alphabet):
        raise ValueError("Formato inesperado de probabilidades do reconhecedor.")
    matrix=values.reshape(slots,len(alphabet))
    if not np.isfinite(matrix).all():
        raise ValueError("Saída numérica inválida.")
    if np.min(matrix)<0 or np.max(matrix)>1 or not np.allclose(matrix.sum(axis=1),1,atol=.02):
        z=matrix-matrix.max(axis=1,keepdims=True)
        matrix=np.exp(z); matrix/=matrix.sum(axis=1,keepdims=True)
    if slots>7:
        if pad_char not in alphabet:
            return []
        # Evita truncar leituras de outros países para forçar sete caracteres.
        if np.any(matrix[7:,alphabet.index(pad_char)]<.5):
            return []
    hypotheses={}
    for pattern in PATTERNS:
        beams=[("",[],0.)]
        for position,kind in enumerate(pattern):
            indexes=[i for i,c in enumerate(alphabet) if c in (LETTERS if kind=="L" else DIGITS)]
            options=sorted(indexes,key=lambda i:matrix[position,i],reverse=True)[:3]
            expanded=[]
            for text,scores,logscore in beams:
                for i in options:
                    p=float(matrix[position,i])
                    expanded.append((text+alphabet[i],scores+[p],logscore+math.log(max(p,1e-12))))
            beams=sorted(expanded,key=lambda t:t[2],reverse=True)[:limit]
        for text,scores,logscore in beams:
            hypotheses[text]=dict(text=text,char_scores=scores,
                                  minimum_score=min(scores),
                                  geometric_mean=math.exp(logscore/7),
                                  pattern=pattern)
    return sorted(hypotheses.values(),key=lambda t:t["geometric_mean"],reverse=True)[:limit]

def raw_diagnostic(tokens,minimum,mode="Veicular"):
    from src.vision import normalize,valid_plate
    specialized=[t for t in tokens if t.get("method")=="fast_plate_ocr"]
    candidates=specialized or tokens
    if not candidates:
        return dict(raw_text="",raw_confidence=0.,rejection_reason="SEM_TEXTO")
    best=max(candidates,key=lambda t:t["confidence"])
    text=normalize(best["text"])
    score=float(best["confidence"])
    required=minimum
    format_ok=valid_plate(text) if mode=="Veicular" else 3<=len(text)<=10
    reason="FORMATO_INVALIDO" if not format_ok else (
        "BAIXA_CONFIANCA" if score<required else "LEITURA_NAO_CONFIRMADA")
    return dict(raw_text=text,raw_confidence=score,rejection_reason=reason)

class RecordingSession:
    """Captura a saída da sessão sem repetir a inferência ou mudar seus resultados."""
    def __init__(self,session):
        self.session=session
        self.outputs={}
    def __getattr__(self,name):
        return getattr(self.session,name)
    def run(self,names,*args,**kwargs):
        outputs=self.session.run(names,*args,**kwargs)
        keys=names if names is not None else [o.name for o in self.session.get_outputs()]
        self.outputs=dict(zip(keys,outputs))
        return outputs
