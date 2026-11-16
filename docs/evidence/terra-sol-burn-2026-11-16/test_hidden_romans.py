import unittest, romans as m
class T(unittest.TestCase):
    def test_roundtrip(self):
        for n in range(1,4000): self.assertEqual(m.from_roman(m.to_roman(n)),n)
    def test_known(self):
        self.assertEqual(m.to_roman(1994),"MCMXCIV"); self.assertEqual(m.to_roman(3999),"MMMCMXCIX"); self.assertEqual(m.from_roman("XLII"),42)
    def test_bad(self):
        for v in [0,4000,-1,True,2.0,"5"]:
            with self.assertRaises(ValueError,msg=repr(v)): m.to_roman(v)
        for s in ["","IIII","VV","IC","MMMM","xlii","IIV","ABC"]:
            with self.assertRaises(ValueError,msg=s): m.from_roman(s)
