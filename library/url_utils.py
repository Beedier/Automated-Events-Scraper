from urllib.parse import urlparse, urlunparse, urlencode


def build_url_with_params(
        base_url,
        scheme=None,
        netloc=None,
        path=None,
        params=None,
        query_params=None,
        fragment=None
):
    """
    Build a complete URL by optionally overriding parts of the base URL
    and appending query parameters.

    Args:
        base_url (str): The base URL to modify.
        scheme (str, optional): Override URL scheme (e.g., 'https').
        netloc (str, optional): Override network location (e.g., 'example.com').
        path (str, optional): Override the path (e.g., '/search').
        params (str, optional): Additional URL params (rarely used).
        query_params (dict, optional): Dictionary of query parameters to append.
        fragment (str, optional): URL fragment identifier (e.g., 'section1').

    Returns:
        str: Fully constructed URL.

    Example:
        build_url_with_params(
            "https://example.com/base",
            path="/search",
            query_params={"q": "architecture", "page": 2}
        )
        # Output: 'https://example.com/search?q=architecture&page=2'
    """
    parsed = urlparse(base_url)
    updated = parsed._replace(
        scheme=scheme or parsed.scheme,
        netloc=netloc or parsed.netloc,
        path=path if path is not None else parsed.path,
        params=params or parsed.params,
        query=urlencode(query_params or {}),
        fragment=fragment or parsed.fragment
    )
    return urlunparse(updated)
