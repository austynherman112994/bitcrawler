import urllib.parse
import requests

import validators

import link_utils
import parsing


def _resolve_relative_links(original_url, links):
    links = [
        urllib.parse.urljoin(original_url, link)
        if link_utils.is_relative(link) else link for link in links]
    return links

def _remove_cross_site_links(original_url, links):
    same_site_links = []
    for link in links:
        if link_utils.is_same_host(link, original_url):
            same_site_links.append(link)
    return same_site_links

class Webpage:
    def __init__(self, url, allowed_by_robots):
        self.url = url
        self.response = None
        self.soup = None
        self.links = None
        self.content_type = None
        self.charset = None
        self.allowed_by_robots = allowed_by_robots

    def __str__(self):
        return str({
            'url': self.url,
            'links': self.links
        })

    @classmethod
    def get_robots(cls, url):
        pass

    @classmethod
    def fetch(cls, url, requests_kwargs=None):
        if not requests_kwargs:
            requests_kwargs = {}
        try:
            return requests.get(url, **requests_kwargs)
        except Exception as e:
            # TODO logging
            raise e
            return None

    @classmethod
    def parse_content_type(cls, content_type_header):
        if content_type_header:
            split_content_type = content_type_header.split(";")
            if len(split_content_type) >= 2:
                return split_content_type[:2]
            elif len(split_content_type) == 1:
                content_type = split_content_type[0]
                return content_type, None
        return None, None

    @classmethod
    def _get_links(cls, url, soup):
        discovered_links = soup.get_links()

        # Append base url to relative links
        base_url = link_utils.get_base_url(url)
        resolved_links = _resolve_relative_links(
            base_url, discovered_links)

        # Remove invalid links
        valid_urls = [url for url in resolved_links if validators.url(url)]
        return valid_urls

    @classmethod
    def get_links(cls, url, soup, cross_site):
        links = cls._get_links(url, soup)

        if cross_site:
            return links
        else:
            return _remove_cross_site_links(url, links)


    def crawl_page(self, cross_site=False):
        self.response = self.fetch(self.url)
        if self.response and self.response.ok:
            self.content_type, self.charset = (
                self.parse_content_type(
                    self.response.headers.get('content-type')))
            self.soup = parsing.HtmlParser(self.response.text)
            self.links = self.get_links(self.url, self.soup, cross_site)
        return self

# print(validators.url("http://python.org"))
# print(Webpage("http://python.org", True).crawl_page())
