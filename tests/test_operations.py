import unittest
import sys
sys.path.append('calculator')
import operations

class TestOperations(unittest.TestCase):

    def test_add(self):
        self.assertEqual(operations.add(1, 2), 3)
        self.assertEqual(operations.add(-1, 1), 0)
        self.assertEqual(operations.add(-1, -1), -2)

    def test_subtract(self):
        self.assertEqual(operations.subtract(2, 1), 1)
        self.assertEqual(operations.subtract(-1, 1), -2)
        self.assertEqual(operations.subtract(-1, -1), 0)

    def test_multiply(self):
        self.assertEqual(operations.multiply(2, 3), 6)
        self.assertEqual(operations.multiply(-1, 1), -1)
        self.assertEqual(operations.multiply(-1, -1), 1)

    def test_divide(self):
        self.assertEqual(operations.divide(6, 3), 2)
        self.assertEqual(operations.divide(-1, 1), -1)
        with self.assertRaises(ValueError):
            operations.divide(1, 0)

    def test_sin(self):
        self.assertAlmostEqual(operations.sin(90), 1)
        self.assertAlmostEqual(operations.sin(0), 0)

    def test_cos(self):
        self.assertAlmostEqual(operations.cos(0), 1)
        self.assertAlmostEqual(operations.cos(90), 0)

    def test_tan(self):
        self.assertAlmostEqual(operations.tan(45), 1)
        self.assertAlmostEqual(operations.tan(0), 0)

    def test_log(self):
        self.assertAlmostEqual(operations.log(100), 2)
        with self.assertRaises(ValueError):
            operations.log(0)

    def test_ln(self):
        self.assertAlmostEqual(operations.ln(1), 0)
        with self.assertRaises(ValueError):
            operations.ln(0)

    def test_sqrt(self):
        self.assertEqual(operations.sqrt(4), 2)
        with self.assertRaises(ValueError):
            operations.sqrt(-1)

    def test_power(self):
        self.assertEqual(operations.power(2, 3), 8)
        self.assertEqual(operations.power(2, 0), 1)

if __name__ == '__main__':
    unittest.main()
