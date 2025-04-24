import unittest
from bs4 import BeautifulSoup
from library import extract_clean_text  # replace with your actual module

class TestExtractCleanText(unittest.TestCase):

    def test_basic_extraction(self):
        html = "<html><body><p>Hello</p><p>World</p></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "Hello\nWorld")

    def test_nested_tags(self):
        html = "<div><h1>Title</h1><p>Some <b>bold</b> text.</p></div>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "Title\nSome\nbold\ntext.")

    def test_whitespace_handling(self):
        html = "<p>   First    </p><p>\nSecond\t</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "First\nSecond")

    def test_empty_html(self):
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertIsNone(result)

    def test_non_soup_input(self):
        self.assertIsNone(extract_clean_text("not_soup"))

    def test_none_input(self):
        self.assertIsNone(extract_clean_text(None))

    def test_invalid_html(self):
        html = "<div><p>Unclosed tag"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "Unclosed tag")

    def test_line_breaks_removed(self):
        html = "<p>Line1<br/>Line2</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "Line1\nLine2")

    def test_special_characters(self):
        html = "<p>Test &amp; check</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertEqual(result, "Test & check")

    def test_only_tags_no_text(self):
        html = "<div><br/><hr/></div>"
        soup = BeautifulSoup(html, "html.parser")
        result = extract_clean_text(soup)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
