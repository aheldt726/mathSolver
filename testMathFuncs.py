import unittest
from interpreters import str_to_eqs


class StringToFunc(unittest.TestCase):
    def test_non_linear_to_none(self):
        self.assertEqual(None, str_to_eqs("3x^2")[1])
        self.assertEqual(None, str_to_eqs("3x^2+4*y")[1])
        self.assertEqual(None, str_to_eqs("3x^2+4*y+3*x")[1])
        self.assertEqual(None, str_to_eqs("3x^-2")[1])
        #Well now I'm interested, how does negative work?


    def test_linear_to_not_none(self):
        self.assertNotEqual(None, str_to_eqs("3x")[1])
        self.assertNotEqual(None, str_to_eqs("3x+4y")[1])




if __name__ == '__main__':
    unittest.main()
