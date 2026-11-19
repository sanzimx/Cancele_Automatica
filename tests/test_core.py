"""Testes de comportamento. Não exigem câmera, serial ou download de pesos."""
import unittest
import numpy as np
from src.vision import Params, normalize, valid_plate, select_candidate, preprocess, map_box
from src.metrics import summarize, distance

def token(text,x=0,y=0,w=100,h=30,confidence=.9):
    return dict(text=text,confidence=confidence,
                box=[[x,y],[x+w,y],[x+w,y+h],[x,y+h]])

class VisionTests(unittest.TestCase):
    def test_formats(self):
        self.assertTrue(valid_plate("ABC-1234"))
        self.assertTrue(valid_plate("ABC1D23"))
        self.assertFalse(valid_plate("HWN"))
        self.assertEqual(normalize(" rm 10-c "),"RM10C")

    def test_unknown_plate_is_read_but_denied(self):
        chosen,status=select_candidate([token("XYZ9A88")],{"ABC1D23"},Params())
        self.assertEqual(chosen["text"],"XYZ9A88")
        self.assertEqual(status,"NEGADO")

    def test_no_substring_authorization(self):
        chosen,status=select_candidate([token("CAMERAHWN")],{"HWN"},Params())
        self.assertIsNone(chosen)
        self.assertEqual(status,"SEM_LEITURA")

    def test_low_confidence(self):
        chosen,_=select_candidate([token("ABC1D23",confidence=.2)],{"ABC1D23"},Params())
        self.assertIsNone(chosen)

    def test_distant_fragments_not_combined(self):
        chosen,_=select_candidate([token("ABC",0),token("1D23",800)],{"ABC1D23"},Params())
        self.assertIsNone(chosen)

    def test_adjacent_fragments(self):
        chosen,status=select_candidate([token("ABC",0,w=60),token("1D23",70,w=80)],{"ABC1D23"},Params())
        self.assertEqual(chosen["text"],"ABC1D23")
        self.assertEqual(status,"AUTORIZADO")

    def test_two_plates_are_ambiguous(self):
        chosen,status=select_candidate([token("ABC1D23"),token("XYZ9A88",500)],{"ABC1D23"},Params())
        self.assertIsNone(chosen)
        self.assertEqual(status,"AMBIGUO")

    def test_coordinate_mapping_after_crop_resize(self):
        image=np.zeros((200,400,3),np.uint8)
        _,mapping=preprocess(image,Params(width=400,roi=(.25,.25,.75,.75)))
        mapped=map_box([[0,0],[400,200]],mapping,image.shape)
        self.assertEqual(mapped,[[100,50],[300,150]])

    def test_invalid_roi(self):
        with self.assertRaises(ValueError):
            preprocess(np.zeros((100,100,3),np.uint8),Params(roi=(.8,0,.2,1)))

class MetricTests(unittest.TestCase):
    def test_distance(self):
        self.assertEqual(distance("ABC1234","ABC1235"),1)
        self.assertEqual(distance("ABC",""),3)

    def test_false_authorization_and_failed_case(self):
        rows=[
          dict(expected_plate="ABC1D23",predicted_plate="ABC1D23",expected_authorized=True,predicted_authorized=True,elapsed_ms=100,error=""),
          dict(expected_plate="",predicted_plate="ABC1D23",expected_authorized=False,predicted_authorized=True,elapsed_ms=200,error=""),
          dict(expected_plate="",predicted_plate="",expected_authorized=False,predicted_authorized=False,elapsed_ms=0,error="RuntimeError")]
        result=summarize(rows)
        self.assertEqual(result["false_authorizations"],1)
        self.assertEqual(result["execution_errors"],1)
        self.assertAlmostEqual(result["exact_match_all"],1/3)
        self.assertEqual(result["p95_pipeline_ms"],200)

if __name__=="__main__":
    unittest.main()
