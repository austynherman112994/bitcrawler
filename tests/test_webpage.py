import pytest
from unittest.mock import patch

from bitcrawler import webpage

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
        "http://python.org",
        "http://python.org/path/1234",
        "http://yahoo.com/search"
    ]
    original_url_2 = "http://python.org/"
    results_2 = [
        "http://python.org/",
        "http://python.org/",
        "http://python.org/path/1234",
        "http://yahoo.com/search"
    ]

    original_url_3 = "http://python.org:8080"
    results_3 = [
        "http://python.org:8080",
        "http://python.org:8080",
        "http://python.org:8080/path/1234",
        "http://yahoo.com/search"
    ]
    original_url_4 = "http://python.org:8080/"
    results_4 = [
        "http://python.org:8080/",
        "http://python.org:8080/",
        "http://python.org:8080/path/1234",
        "http://yahoo.com/search"
    ]

    input_links = ["", None, "path/1234", "http://yahoo.com/search"]
    links = webpage.Webpage._resolve_relative_links(original_url_1, input_links)
    for index, link in enumerate(links):
        assert link == results_1[index]
    links = webpage.Webpage._resolve_relative_links(original_url_2, input_links)
    for index, link in enumerate(links):
        assert link == results_2[index]
    links = webpage.Webpage._resolve_relative_links(original_url_3, input_links)
    for index, link in enumerate(links):
        assert link == results_3[index]
    links = webpage.Webpage._resolve_relative_links(original_url_4, input_links)
    for index, link in enumerate(links):
        assert link == results_4[index]
