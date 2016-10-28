import unittest

import parse_input

class TestParseInput(unittest.TestCase):

    def test_line_is_comment(self):
        # Empty line.
        self.assertTrue(parse_input.line_is_comment(''))
        # Line starting with '#'.
        self.assertTrue(parse_input.line_is_comment('# Comment.'))
        # For Chaco, line starting with '%'.
        self.assertTrue(parse_input.line_is_comment('% Comment.'))

        # Normal lines.
        self.assertFalse(parse_input.line_is_comment('This is not comment.'))
        self.assertFalse(parse_input.line_is_comment('123 456'))

    def test_to_num(self):
        self.assertEqual(123, parse_input.to_num('123'))
        self.assertEqual(123.456, parse_input.to_num('123.456'))


if __name__ == '__main__':
    unittest.main()
