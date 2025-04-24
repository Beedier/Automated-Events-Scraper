import unittest
from library import parse_json_to_dict

class TestParseJsonToDict(unittest.TestCase):
    def test_valid_json_object(self):
        self.assertEqual(parse_json_to_dict('{"a":1}'), {"a": 1})

    def test_valid_json_array(self):
        self.assertEqual(parse_json_to_dict('[1, 2, 3]'), [1, 2, 3])

    def test_markdown_code_block(self):
        input_data = '```json\n{"key": "value"}\n```'
        self.assertEqual(parse_json_to_dict(input_data), {"key": "value"})

    def test_markdown_without_lang(self):
        input_data = '```\n{"x":42}\n```'
        self.assertEqual(parse_json_to_dict(input_data), {"x": 42})

    def test_escaped_json_string(self):
        escaped = '{"message": "hello\\nworld"}'
        self.assertEqual(parse_json_to_dict(escaped), {"message": "hello\nworld"})

    def test_json_in_noisy_text(self):
        noisy = "random text before {\"valid\":true} random after"
        self.assertEqual(parse_json_to_dict(noisy), {"valid": True})

    def test_multiple_json_objects(self):
        multiple = '{"one": 1} {"two": 2}'
        self.assertEqual(parse_json_to_dict(multiple), {"one": 1})

    def test_empty_string_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            parse_json_to_dict("")

    def test_invalid_json_raise_value_error_exception(self):
        with self.assertRaises(ValueError):
            parse_json_to_dict('```json```')

if __name__ == "__main__":
    unittest.main()
