"""Comportamento multiveículo com detector/OCR simulados, sem baixar pesos."""
import unittest
from types import SimpleNamespace
import numpy as np
from src.vision import Params
from src.automatic_pipeline import AutomaticPipeline,aggregate_status,expanded_crop,suppress_duplicates

def detection(x0,y0,x1,y1,confidence=.9):
    return SimpleNamespace(confidence=confidence,
        bounding_box=SimpleNamespace(x1=x0,y1=y0,x2=x1,y2=y1))

class FakeDetector:
    def __init__(self,boxes):
        self.boxes=boxes
        self.calls=0
    def predict(self,image):
        self.calls+=1
        return self.boxes

class FakeOCR:
    def __init__(self):
        self.params=[]
    def analyze(self,image,params,authorized):
        self.params.append(params)
        return dict(plate="ABC1D23",status="AUTORIZADO",confidence=.95,elapsed_ms=5,
                    tokens=[],prepared=np.zeros((60,320),np.uint8),overlay=image.copy())

class AutomaticTests(unittest.TestCase):
    def test_two_authorized_vehicles_never_choose_one(self):
        self.assertEqual(aggregate_status([{"status":"AUTORIZADO"}]*2,2),"MULTIPLAS_PLACAS")

    def test_one_authorized_and_one_unreadable_never_authorize(self):
        self.assertEqual(aggregate_status([{"status":"AUTORIZADO"},{"status":"SEM_LEITURA"}],2),
                         "MULTIPLAS_PLACAS")

    def test_missing_detection_has_no_ocr_fallback(self):
        pipeline=AutomaticPipeline(FakeOCR())
        pipeline.detector=FakeDetector([])
        result=pipeline.analyze(np.zeros((400,800,3),np.uint8),Params(),{"ABC1D23"})
        self.assertEqual(result["status"],"SEM_PLACA")
        self.assertEqual(pipeline.ocr.params,[])

    def test_boxes_return_to_original_image_after_search_roi(self):
        pipeline=AutomaticPipeline(None)
        pipeline.detector=FakeDetector([detection(20,10,120,50)])
        boxes=pipeline.detect(np.zeros((400,800,3),np.uint8),Params(roi=(.25,.25,.75,.75)))
        self.assertEqual(boxes[0]["box"],[220,110,320,150])

    def test_overlapping_windows_do_not_duplicate_same_plate(self):
        pipeline=AutomaticPipeline(None)
        pipeline.detector=FakeDetector([detection(20,20,80,50)])
        # Full-frame + 4 detail calls are made; their coordinates are offset per window.
        pipeline.detect(np.zeros((400,800,3),np.uint8),Params(detector_detail=True))
        self.assertEqual(pipeline.detector.calls,5)
        boxes=[dict(box=[20,20,80,50],confidence=.9),
               dict(box=[22,21,81,51],confidence=.8),
               dict(box=[200,20,260,50],confidence=.85)]
        self.assertEqual(len(suppress_duplicates(boxes)),2)

    def test_confidence_filters_detector_not_ocr(self):
        pipeline=AutomaticPipeline(None)
        pipeline.detector=FakeDetector([detection(10,10,100,40,.2)])
        self.assertEqual(pipeline.detect(np.zeros((400,800,3),np.uint8),
                                        Params(detector_confidence=.35)),[])

    def test_crop_expansion_stays_in_image(self):
        self.assertEqual(expanded_crop([0,0,100,40],(40,100,3)),(0,0,100,40))

    def test_per_plate_ocr_is_separate_and_recursion_disabled(self):
        ocr=FakeOCR()
        pipeline=AutomaticPipeline(ocr)
        pipeline.detector=FakeDetector([detection(20,30,150,70),detection(300,100,430,140)])
        result=pipeline.analyze(np.zeros((400,800,3),np.uint8),Params(),{"ABC1D23"})
        self.assertEqual(len(ocr.params),2)
        self.assertTrue(all(not p.auto_detect for p in ocr.params))
        self.assertNotEqual(ocr.params[0].roi,ocr.params[1].roi)
        self.assertEqual(result["detected_count"],2)
        self.assertEqual(result["plate"],"")
        self.assertEqual(result["status"],"MULTIPLAS_PLACAS")
        # Os tokens não são concatenados entre placas distintas.
        self.assertEqual(len(result["plates"]),2)

    def test_single_plate_preserves_ocr_decision(self):
        pipeline=AutomaticPipeline(FakeOCR())
        pipeline.detector=FakeDetector([detection(20,30,150,70)])
        result=pipeline.analyze(np.zeros((400,800,3),np.uint8),Params(),{"ABC1D23"})
        self.assertEqual(result["plate"],"ABC1D23")
        self.assertEqual(result["status"],"AUTORIZADO")

if __name__=="__main__":
    unittest.main()
