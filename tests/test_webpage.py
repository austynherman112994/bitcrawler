import pytest
from unittest.mock import patch

from bitcrawler import parsing
from bitcrawler import webpage
from bitcrawler import robots

@patch('requests.get')
def test_fetch__with_kwargs(requests_get_mock):
    url = "http://python.org"
    requests_kwargs = {'timeout': 5}
    webpage.Webpage.fetch(url, **requests_kwargs)

    requests_get_mock.assert_called_with(url, **requests_kwargs)

@patch('requests.get')
def test_fetch(requests_get_mock):
    url = "http://python.org"
    webpage.Webpage.fetch(url)

    requests_get_mock.assert_called_with(url, **{})

def test_parse_mime_type():
    mime_types = [
        "text/html;charset=utf-8",
        "text/html; charset=utf-8",
        "text/html",
        "",
        None
    ]
    mime_results = [
        ("text/html", "charset=utf-8"),
        ("text/html", "charset=utf-8"),
        ("text/html", None),
        (None, None),
        (None, None)
    ]
    for index, mime_type in enumerate(mime_types):
        result = webpage.Webpage.parse_mime_type(mime_type)
        assert result == mime_results[index]


def test__resolve_relative_links():
    original_url_1 = "http://python.org"
    results_1 = [
        "http://python.org",
        "http://python.org/path/1234",
        "http://yahoo.com/search"
    ]
    original_url_2 = "http://python.org/"
    results_2 = [
        "http://python.org/",
        "http://python.org/path/1234",
        "http://yahoo.com/search"
    ]

    original_url_3 = "http://python.org:8080"
    results_3 = [
        "http://python.org:8080",
        "http://python.org:8080/path/1234",
        "http://yahoo.com/search"
    ]
    original_url_4 = "http://python.org:8080/"
    results_4 = [
        "http://python.org:8080/",
        "http://python.org:8080/path/1234",
        "http://yahoo.com/search"
    ]

    input_links = ["", None, "path/1234", "http://yahoo.com/search"]
    links = webpage.Webpage._resolve_relative_links(original_url_1, input_links)
    assert links.sort() == results_1.sort()
    links = webpage.Webpage._resolve_relative_links(original_url_2, input_links)
    assert links.sort() == results_2.sort()
    links = webpage.Webpage._resolve_relative_links(original_url_3, input_links)
    assert links.sort() == results_3.sort()
    links = webpage.Webpage._resolve_relative_links(original_url_4, input_links)
    assert links.sort() == results_4.sort()


@patch.object(
    parsing.HtmlParser,
    'get_links',
    return_value=[
        "http://python.org/about",
        "http://python.org/123",
        "aaaa",
        "a.rpps",
        "http://python.org/123/!@#$%^&*()"
    ]
)
def test_get_html_links__invalid_url(mock_get_links):
    expected_results = [
        "http://python.org/about",
        "http://python.org/123"
    ]
    page = webpage.Webpage()
    page._fetched = True
    links = page.get_page_links()
    assert links.sort() == expected_results.sort()


# @patch.object(
#     robots.RobotParser,
#     'allowed_by_robots',
#     return_value=False
# )
# @patch.object(
#     robots.RobotParser,
#     '__init__',
#     return_value=None)
# def test_is_allowed_by_robots__no_reppy(mock_reppy, mock_allowed):
#     url = 'http://python.org'
#     cache_test = {'cache_test': 'test1'}
#     request_test = {'request_test': 'test2'}
#     allowed = webpage.Webpage.is_allowed_by_robots(
#         url,
#         reppy_cache_kwargs=cache_test,
#         reppy_request_kwargs=request_test
#     )
#     mock_reppy.assert_called_with(
#             cache_kwargs=cache_test,
#             request_kwargs=request_test)
#     assert allowed == False
