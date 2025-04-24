import unittest
from library import build_url_with_params

class TestBuildUrlWithParams(unittest.TestCase):
    def test_basic_query_append(self):
        url = build_url_with_params("https://example.com", query_params={"a": 1, "b": 2})
        self.assertEqual(url, "https://example.com?a=1&b=2")

    def test_override_path(self):
        url = build_url_with_params("https://example.com/base", path="/new")
        self.assertEqual(url, "https://example.com/new")

    def test_override_scheme_and_netloc(self):
        url = build_url_with_params("http://oldsite.com", scheme="https", netloc="newsite.com")
        self.assertEqual(url, "https://newsite.com")

    def test_full_override(self):
        url = build_url_with_params(
            "http://old.com/oldpath",
            scheme="https",
            netloc="new.com",
            path="/newpath",
            query_params={"x": "y"},
            fragment="top"
        )
        self.assertEqual(url, "https://new.com/newpath?x=y#top")

    def test_fragment_only(self):
        url = build_url_with_params("https://example.com", fragment="section1")
        self.assertEqual(url, "https://example.com#section1")

    def test_no_changes(self):
        url = build_url_with_params("https://example.com")
        self.assertEqual(url, "https://example.com")

    def test_with_params_field(self):
        url = build_url_with_params("https://example.com", params="p")
        self.assertEqual(url, "https://example.com/;p")

    def test_empty_query_params(self):
        url = build_url_with_params("https://example.com", query_params={})
        self.assertEqual(url, "https://example.com")

    def test_query_params_encoding(self):
        url = build_url_with_params("https://example.com", query_params={"q": "hello world"})
        self.assertEqual(url, "https://example.com?q=hello+world")

    def test_override_path_and_query(self):
        url = build_url_with_params("https://example.com/base", path="/search", query_params={"q": "test"})
        self.assertEqual(url, "https://example.com/search?q=test")

if __name__ == "__main__":
    unittest.main()
