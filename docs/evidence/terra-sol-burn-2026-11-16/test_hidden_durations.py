import unittest, durations as m
class T(unittest.TestCase):
    def test_ok(self):
        for s,v in [("1h30m",5400),("45s",45),("2d 3h",183600),("1h 0m 5s",3605),("1H30M",5400),(" 10 m ",600),("0s",0)]:
            self.assertEqual(m.parse_duration(s),v,s)
    def test_bad(self):
        for s in ["","   ","1h1h","5x","-5m","h","1.5h","abc"]:
            with self.assertRaises(ValueError,msg=s): m.parse_duration(s)
