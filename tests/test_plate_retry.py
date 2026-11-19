"""Regras das tentativas adicionais, com reconhecedor simulado."""
import unittest
import numpy as np
from src.vision import Params
from src.plate_retry import retry_plate

class Reader:
    def __init__(self,results):
        self.results=iter(results)
    def recognize(self,image,**kwargs):
        text,score=next(self.results)
        h,w=image.shape
        return [([[0,0],[w,0],[w,h],[0,h]],text,score)]

class RetryTests(unittest.TestCase):
    def run_case(self,results,authorized=()):
        return retry_plate(Reader(results),np.zeros((100,300,3),np.uint8),
                           [20,20,200,65],Params(),authorized)

    def test_does_not_replace_text_from_authorization_list(self):
        result=self.run_case([("XYZ9A88",.9)]*3,["ABC1D23"])
        self.assertEqual(result["plate"],"XYZ9A88")
        self.assertEqual(result["status"],"NEGADO")

    def test_rejects_wrong_length_even_if_registered(self):
        result=self.run_case([("PSZJZ5",.95)]*3,["PSZJZ5"])
        self.assertEqual(result["status"],"SEM_LEITURA")

    def test_low_scores_remain_unreadable(self):
        result=self.run_case([("ABC1D23",.2)]*3,["ABC1D23"])
        self.assertEqual(result["status"],"SEM_LEITURA")

    def test_retry_respects_configured_threshold(self):
        result=self.run_case([("ABC1D23",.65)]*3,["ABC1D23"])
        self.assertEqual(result["status"],"AUTORIZADO")

    def test_conflicting_qualified_readings_are_ambiguous(self):
        result=self.run_case([("ABC1D23",.95),("XYZ9A88",.85),("ABC1D23",.95)],["ABC1D23"])
        self.assertEqual(result["status"],"AMBIGUO")

    def test_exact_high_score_authorization(self):
        result=self.run_case([("ABC1D23",.9)]*3,["ABC1D23"])
        self.assertEqual(result["status"],"AUTORIZADO")

if __name__=="__main__":
    unittest.main()
