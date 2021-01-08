import pytest
from unittest.mock import patch

from bitcrawler import parsing
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


def test_get_same_site_links():
    original_url = "http://python.org/"
    input_links = [
        "http://python.org/",
        "http://python.org:8080/",
        "http://python.org/path/1234",
        "http://about.python.org/path/1234",
        "http://yahoo.com/search"
    ]
    results = [
        "http://python.org/",
        "http://python.org:8080/",
        "http://python.org/path/1234",
        "http://about.python.org/path/1234",
    ]
    links = webpage.Webpage.get_same_site_links(original_url, input_links)

    assert links.sort() == results.sort()

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
def test_get_links__invalid_url(mock_get_links):
    expected_results = [
        "http://python.org/about",
        "http://python.org/123"
    ]
    links = webpage.Webpage.get_links("http://python.org", parsing.HtmlParser(""))
    assert links.sort() == expected_results.sort()



def test_crawl_page():
    pass

def test_():
    pass
# class Webpage:

#
#     def crawl_page(
#             self,
#             user_agent,
#             request_kwargs=None,
#             respect_robots=True,
#             reppy=None,
#             reppy_cache_kwargs=None,
#             reppy_robots_kwargs=None):
#
#         if not request_kwargs:
#             request_kwargs = {}
#         if respect_robots:
#             if not reppy:
#                 reppy = RobotParser(
#                     cache_kwargs=reppy_cache_kwargs,
#                     request_kwargs=reppy_robots_kwargs)
#             self.allowed_by_robots = reppy.allowed_by_robots(self.url)
#
#         if self.allowed_by_robots == False:
#             self.message = f"URL {self.url} is restricted by robots.txt"
#         # Only False should prevent crawling (None should allow.)
#         else:
#             try:
#                 self.response = self.fetch(self.url, **requests_kwargs)
#             except Exception as e:
#                 self.message = "An error occurred while attempting to fetch {self.url}: {e}"
#                 logging.error(self.message)
#                 self.error = e
#
#             if self.response
#                 if self.response.ok:
#                     self.content_type, self.charset = (
#                         self.parse_content_type(
#                             self.response.headers.get('content-type')))
#
#                     if self.content_type == 'text/html':
#                         self.soup = parsing.HtmlParser(self.response.text, "html.parser")
#                         self.links = self.get_links(self.url, self.soup)
#                         self.same_site_links = (
#                             self.get_same_site_links(self.url, self.links))
#                 else:
#                     self.message = f"URL %s returned a {self.response.status_code} status code."
#         return self
