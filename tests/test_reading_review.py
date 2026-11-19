import string
import unittest
import numpy as np
from src.reading_review import constrained_candidates,raw_diagnostic,RecordingSession

ALPHABET=string.ascii_uppercase+string.digits+"_"

def distribution(text):
    values=np.full((9,len(ALPHABET)),.0001)
    for i,char in enumerate(text+"_"*(9-len(text))):
        values[i,ALPHABET.index(char)]=.95
    values/=values.sum(axis=1,keepdims=True)
    return values

class ReviewTests(unittest.TestCase):
    def test_general_pattern_uses_actual_digit_score_without_boosting(self):
        values=distribution("ABC1DZ3")
        values[5]=.00001
        values[5,ALPHABET.index("Z")]=.8
        values[5,ALPHABET.index("2")]=.19
        values[5]/=values[5].sum()
        result=constrained_candidates(values,ALPHABET,9,"_")
        self.assertEqual(result[0]["text"],"ABC1D23")
        self.assertLess(result[0]["minimum_score"],.25)

    def test_old_brazilian_layout(self):
        result=constrained_candidates(distribution("ABC1234"),ALPHABET,9,"_")
        self.assertEqual(result[0]["text"],"ABC1234")

    def test_no_truncation_of_long_foreign_reading(self):
        result=constrained_candidates(distribution("ABC123456"),ALPHABET,9,"_")
        self.assertEqual(result,[])

    def test_unexpected_output_does_not_invent_probabilities(self):
        with self.assertRaises(ValueError):
            constrained_candidates(np.zeros((2,3)),ALPHABET,9,"_")

    def test_invalid_format_preserves_raw_score(self):
        d=raw_diagnostic([dict(text="ABC1DZ3",confidence=.796,method="fast_plate_ocr")],.6)
        self.assertEqual(d["rejection_reason"],"FORMATO_INVALIDO")
        self.assertEqual(d["raw_text"],"ABC1DZ3")
        self.assertAlmostEqual(d["raw_confidence"],.796)

    def test_valid_format_but_low_score(self):
        d=raw_diagnostic([dict(text="ABC1D23",confidence=.4,method="fast_plate_ocr")],.6)
        self.assertEqual(d["rejection_reason"],"BAIXA_CONFIANCA")

    def test_session_capture_does_not_change_inference_output(self):
        class Fake:
            def run(self,names,inputs):
                return [np.array([1.,2.])]
        session=RecordingSession(Fake())
        result=session.run(["plate"],{"input":np.array([0])})
        np.testing.assert_array_equal(session.outputs["plate"],result[0])

if __name__=="__main__":
    unittest.main()
