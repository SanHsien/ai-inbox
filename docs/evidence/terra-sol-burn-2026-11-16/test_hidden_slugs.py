import unittest, slugs as m
class T(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(m.slugify("Hello, World!"),"hello-world")
        self.assertEqual(m.slugify("Café über naïve"),"cafe-uber-naive")
        self.assertEqual(m.slugify("  --a__b--  "),"a-b")
        self.assertEqual(m.slugify("!!!"),"n-a")
        self.assertEqual(m.slugify(""),"n-a")
    def test_trunc(self):
        self.assertEqual(m.slugify("alpha beta gamma",max_len=12),"alpha-beta")
        self.assertEqual(m.slugify("alpha beta gamma",max_len=10),"alpha-beta")
        self.assertEqual(m.slugify("supercalifragilistic",max_len=5),"super")
        r=m.slugify("one two three four five six seven",max_len=15); self.assertFalse(r.endswith("-")); self.assertLessEqual(len(r),15)
    def test_bad(self):
        with self.assertRaises(ValueError): m.slugify("x",max_len=0)
