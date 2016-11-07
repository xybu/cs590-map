import unittest

import utils_input

class TestUtilsInput(unittest.TestCase):

    def test_to_num(self):
        self.assertEqual(3.14, utils_input.to_num('3.14'))
        self.assertEqual(3, utils_input.to_num('3'))
        self.assertIsInstance(utils_input.to_num('3'), int)
        self.assertRaises(ValueError, utils_input.to_num, '3.1.4')

    def test_line_is_comment(self):
        self.assertTrue(utils_input.line_is_comment('# Hello world!'))
        self.assertTrue(utils_input.line_is_comment('% Hello world!'))
        self.assertTrue(utils_input.line_is_comment(''))
        self.assertFalse(utils_input.line_is_comment('123'))


if __name__ == '__main__':
    unittest.main()
