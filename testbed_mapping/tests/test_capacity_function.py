import unittest

import capacity_function

class TestCapacityFunction(unittest.TestCase):

    SAMPLE_COEFFS = [
        [392.0668, 383.8597],
        [5.7498, 449.099, 4061.2926]
    ]

    def test_linear(self):
        x = 15
        coeffs = self.SAMPLE_COEFFS[0]
        expected =  x * coeffs[0] + coeffs[1]
        f = capacity_function.CapacityFunction(coefficients=coeffs, high_order_first=True)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

    def test_square(self):
        x = 23
        coeffs = self.SAMPLE_COEFFS[1]
        expected = x * x * coeffs[0] + x * coeffs[1] + coeffs[2]
        f = capacity_function.CapacityFunction(coefficients=coeffs, high_order_first=True)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

    def test_square_low_order(self):
        x = 26
        coeffs = self.SAMPLE_COEFFS[1]
        expected = x * x * coeffs[0] + x * coeffs[1] + coeffs[2]
        f = capacity_function.CapacityFunction(coefficients=coeffs[::-1], high_order_first=False)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

if __name__ == '__main__':
    unittest.main()
