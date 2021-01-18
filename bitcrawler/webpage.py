"""This module provides functionality for fetching a webpage and stores
relevant ojects from page retrieval.
"""
import urllib.parse
import logging
import requests

import validators

import parsing
import robots
import link_utils

log = logging.getLogger('bitcrawler').addHandler(logging.NullHandler())

class Webpage:
    """TODO: Docstring
    """
    def __init__(self, url):
        self.url = url
        self.response = None
        self.soup = None
        self.links = None
        self.same_site_links = None
        self.allowed_by_robots = None
        self.message = None
        self.error = None

    def __str__(self):
        return str({
            'url': self.url,
        })

    @classmethod
    def fetch(cls, url, **requests_kwargs):
        """TODO: Docstring

        Use requests sessions for more  functionality.
        """
        if not requests_kwargs:
            requests_kwargs = {}
        return requests.get(url, **requests_kwargs)

    @classmethod
    def parse_mime_type(cls, content_type_header):
        """TODO: Docstring
        """
        if content_type_header:
            split_content_type = content_type_header.split(";")
            if len(split_content_type) >= 2:
                return split_content_type[0], split_content_type[1].strip()
            elif len(split_content_type) == 1:
                content_type = split_content_type[0]
                return content_type, None
        return None, None

    @classmethod
    def _resolve_relative_links(cls, original_url, links):
        """TODO: Docstring
        """
        links = list(set(
            urllib.parse.urljoin(original_url, link)
            if link_utils.is_relative(link) else link for link in links))
        return links

    @classmethod
    def get_same_site_links(cls, original_url, links):
        """TODO: Docstring
        """
        return list(set(
                    link for link in links
                    if link_utils.is_same_domain(link, original_url)))

    @classmethod
    def get_links(cls, url, soup):
        """TODO: Docstring
        """
        discovered_links = soup.get_links()

        # Append base url to relative links
        base_url = link_utils.get_base_url(url)
        resolved_links = cls._resolve_relative_links(
            base_url, discovered_links)

        # Remove invalid links
        valid_urls = list(set(
            url for url in resolved_links if validators.url(url)))
        return valid_urls

    @classmethod
    def is_allowed_by_robots(
            cls,
            url,
            reppy=None,
            reppy_cache_kwargs=None,
            reppy_request_kwargs=None):
        """TODO: Docstring
        """

        if not reppy:
            reppy = robots.RobotParser(
                cache_kwargs=reppy_cache_kwargs,
                request_kwargs=reppy_request_kwargs)
        return reppy.allowed_by_robots(url)

    def crawl_page(
            self,
            user_agent,
            request_kwargs=None,
            respect_robots=True,
            reppy=None,
            reppy_cache_kwargs=None,
            reppy_request_kwargs=None):
        """TODO: Docstring
        """
        if not request_kwargs:
            request_kwargs = {}

        if respect_robots:
            self.allowed_by_robots = self.is_allowed_by_robots(
                self.url, reppy=reppy, reppy_cache_kwargs=reppy_cache_kwargs,
                reppy_request_kwargs=reppy_request_kwargs)

        # Only False should prevent crawling (None should allow.)
        if self.allowed_by_robots is False:
            self.message = f"URL {self.url} is restricted by robots.txt"
        else:
            try:
                self.response = self.fetch(self.url, **request_kwargs)
            except Exception as err:
                self.message = (
                    "An error occurred while attempting to fetch "
                    f"{self.url}: {err}")
                logging.error(self.message)
                self.error = err

            if self.response:
                if self.response.ok:
                    # Second param will be charset for text/html docs
                    content_type, _ = (
                        self.parse_mime_type(
                            self.response.headers.get('content-type')))

                    if content_type == 'text/html':
                        self.soup = parsing.HtmlParser(self.response.text, "html.parser")
                        self.links = self.get_links(self.url, self.soup)
                        self.same_site_links = (
                            self.get_same_site_links(self.url, self.links))
                else:
                    self.message = f"URL %s returned a {self.response.status_code} status code."
        return self
