import unittest

import pm_model

class TestCapacityFunction(unittest.TestCase):

    SAMPLE_COEFFS = [
        [392.0668, 383.8597],
        [5.7498, 449.099, 4061.2926]
    ]

    def test_linear(self):
        x = 15
        coeffs = self.SAMPLE_COEFFS[0]
        expected =  x * coeffs[0] + coeffs[1]
        f = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs, high_order_first=True)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

    def test_square(self):
        x = 27
        coeffs = self.SAMPLE_COEFFS[1]
        expected = x * x * coeffs[0] + x * coeffs[1] + coeffs[2]
        f = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs, high_order_first=True)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

    def test_square_low_order(self):
        x = 26
        coeffs = self.SAMPLE_COEFFS[1]
        expected = x * x * coeffs[0] + x * coeffs[1] + coeffs[2]
        f = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs[::-1], high_order_first=False)
        self.assertEqual(expected, f.eval(x), 'Evaluated value of function is not equal expected.')

    def test_equal(self):
        coeffs = self.SAMPLE_COEFFS[1]
        f1 = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs, high_order_first=True)
        f2 = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs[::-1], high_order_first=False)
        self.assertTrue(f1, f2)

    def test_repr(self):
        """ Make sure __repr__ has no syntax problem. """
        coeffs = self.SAMPLE_COEFFS[1]
        f = pm_model.CapacityFunction(domain=(0, 100), coefficients=coeffs[::-1], high_order_first=False)
        self.assertIsInstance(str(f), str)

class TestMachineObject(unittest.TestCase):

    def test_equal(self):
        params = {'max_cpu_share': 400, 'min_switch_cpu_share': 10, 'max_switch_cpu_share': 130, 'coefficients': [4000, 400, 4]}
        pm1 = pm_model.Machine(pm_id=0, **params)
        pm2 = pm_model.Machine(pm_id=1, **params)
        self.assertEqual(pm1, pm2)

    def test_not_equal(self):
        params = {'max_cpu_share': 400, 'min_switch_cpu_share': 10, 'max_switch_cpu_share': 130, 'coefficients': [4000, 400, 4]}
        pm1 = pm_model.Machine(pm_id=0, **params)
        params['max_switch_cpu_share'] = 11
        pm2 = pm_model.Machine(pm_id=1, **params)
        self.assertNotEqual(pm1, pm2)

    def test_in_list(self):
        params = {'max_cpu_share': 400, 'min_switch_cpu_share': 10, 'max_switch_cpu_share': 130, 'coefficients': [4000, 400, 4]}
        pm = pm_model.Machine(pm_id=0, **params)
        pms = [pm_model.Machine(pm_id=1, **params)]
        self.assertIn(pm, pms)

if __name__ == '__main__':
    unittest.main()
