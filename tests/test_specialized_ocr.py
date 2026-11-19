"""Validação da decisão do OCR especializado, sem baixar modelos."""
import unittest
from types import SimpleNamespace
from src.specialized_ocr import interpret

def pred(text,probs):
    return SimpleNamespace(plate=text,char_probs=probs)

class SpecializedTests(unittest.TestCase):
    def test_registration_does_not_rewrite_reading(self):
        text,score,status=interpret(pred("XYZ9A88",[.95]*7),.6,{"ABC1D23"})
        self.assertEqual(text,"XYZ9A88")
        self.assertEqual(status,"NEGADO")

    def test_weak_character_blocks_authorization(self):
        text,score,status=interpret(pred("ABC1D23",[.99]*6+[.2]),.6,{"ABC1D23"})
        self.assertEqual(status,"SEM_LEITURA")

    def test_padding_ignored_and_format_checked(self):
        text,score,status=interpret(pred("ABC1D23__", [.95]*7+[.99,.99]),.6,{"ABC1D23"})
        self.assertEqual(status,"AUTORIZADO")
        self.assertEqual(text,"ABC1D23")

    def test_missing_scores_fail_explicitly(self):
        with self.assertRaises(ValueError):
            interpret(pred("ABC1D23",[]),.6,{"ABC1D23"})

    def test_free_registration_preserves_non_vehicle_format(self):
        text,score,status=interpret(pred("ABC1DZ3",[.95]*7),.6,{"ABC1DZ3"},"Identificadores")
        self.assertEqual(text,"ABC1DZ3")
        self.assertEqual(status,"AUTORIZADO")

    def test_free_registration_does_not_change_other_characters(self):
        text,score,status=interpret(pred("TESTE123",[.95]*8),.6,{"TESTE128"},"Identificadores")
        self.assertEqual(text,"TESTE123")
        self.assertEqual(status,"NEGADO")

    def test_free_registration_still_rejects_low_confidence(self):
        text,score,status=interpret(pred("ABC1DZ3",[.45]*7),.6,{"ABC1DZ3"},"Identificadores")
        self.assertEqual(status,"SEM_LEITURA")

    def test_selected_threshold_has_no_hidden_floor(self):
        text,score,status=interpret(pred("ABC1DZ3",[.479]*7),.4,{"ABC1DZ3"},"Identificadores")
        self.assertEqual(status,"AUTORIZADO")
        self.assertAlmostEqual(score,.479)

    def test_same_reading_rejected_at_higher_threshold(self):
        text,score,status=interpret(pred("ABC1DZ3",[.479]*7),.6,{"ABC1DZ3"},"Identificadores")
        self.assertEqual(status,"SEM_LEITURA")

if __name__=="__main__":
    unittest.main()
