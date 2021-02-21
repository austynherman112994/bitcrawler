"""This module provides functionality for fetching a webpage and stores
relevant ojects from page retrieval.
"""
import urllib.parse
import logging
import requests

import validators

from . import parsing
from . import robots
from . import link_utils

log = logging.getLogger('bitcrawler')


class Webpage:
    """Webpage provides the ability to fetch a webpage. Stores
    data from the retrieval of the page.
    """
    def __init__(self):
        """ Initializes Webpage.

        Args:
            url (str): The URL associated with the webpage.
        """
        self.url = None
        self.response = None
        self.links = None
        self.allowed_by_robots = None
        self.message = None
        self.error = None
        self._fetched = False

    @classmethod
    def fetch(cls, url, **requests_kwargs):
        """Fetches the webpage for the URL using the requests library.

        Args:
            url (str): The target URL.
            **requests_kwargs (kwargs, optional): Any additional parameters
                to pass onto the reqeusts library.

        Returns:
            obj requests.Response: The response from the web request.

        Raises:
            Exception: Can raise a variety of exceptions. See requests library
            for more details.

        """
        if not requests_kwargs:
            requests_kwargs = {}
        return requests.get(url, **requests_kwargs)


    @classmethod
    def parse_mime_type(cls, mime_type):
        """Parses a mime type into its content type and parameters.

        Args:
            url (str): The target URL.
            **requests_kwargs (kwargs, optional): Any additional parameters
                to pass onto the reqeusts library.

        Returns:
            tuple:
                str: The type of the content.
                str: The content type parameters.

        Examples:
            >>> parse_mime_type("text/html; encoding=utf-8")
            ("text/html", "encoding=utf-8",)

        """
        if mime_type:
            split_mime_type = mime_type.split(";")
            if len(split_mime_type) >= 2:
                return split_mime_type[0], split_mime_type[1].strip()
            elif len(split_mime_type) == 1:
                content_type = split_mime_type[0]
                return content_type, None
        return None, None


    @classmethod
    def _resolve_relative_links(cls, original_url, links):
        """Converts any relative links into full links.

        Leaves any non relative links unmodified.

        Args:
            original_url (str): The original url the links originated from.
            links (list): A list of links.

        Returns:
            list: A list of links where relative links are now full links.

        Examples:
            >>> _resolve_relative_links(
            >>>    "http://python.org"
            >>>    [
            >>>        "http://python.org/about",
            >>>        "/test",
            >>>        "http://pandas.com"
            >>>    ]
            >>> )
            ["http://python.org/about", "http://python.org/test", "http://pandas.com"]

        """
        links = list(set(
            urllib.parse.urljoin(original_url, link)
            if link_utils.LinkUtils.is_relative(link) else link for link in links))
        return links


    @classmethod
    def get_html_links(cls, url, html):
        """Parses links from an html document.

        Args:
            url (str): The target URL.
            html (str): the html document.

        Returns:
            list: A list containing all valid urls found in the html.

        """
        soup = parsing.HtmlParser(html, "html.parser")
        discovered_links = soup.get_links()

        # Append base url to relative links
        base_url = link_utils.LinkUtils.get_base_url(url)
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
            user_agent,
            reppy=None,
            request_kwargs=None):
        """Determine if a page is crawlable by robots.txt.

        Leverages the Reppy library for retrieval and parsing of robots.txt.
i
        Args:
            url (str): The target URL.
            user_agent (str): The user agent being used to crawl the page.
            reppy (:obj:robots.RobotParser, optional): A robots parsing object.
            request_kwargs (dict, optional): requests.get kwargs for fetching the
                robots.txt file.

        Returns:
            bool: True if the page is allowed by robots.txt. Otherwise False.

        """

	    ### TODO See what errors can bubble up from this reppy api

        try:
            if not reppy:
                reppy = robots.ReppyUtils
                allowed = reppy.allowed(url, user_agent, **request_kwargs)
            else:
                allowed = reppy.allowed(url, user_agent)
        except Exception as err:
            log.exception(err)
            allowed = True
        return allowed


    def get_page_links(self):
        """Extracts links from a page.

        Only supports documents with a content type of 'text/html'.
        TODO: Add further support for other doc types.

        Returns:
            list(str): A list of links from the page.

        """
        if self.response:
            if self.response.ok:
                # Second param will be charset for text/html docs
                content_type, _ = (
                    self.parse_mime_type(
                        self.response.headers.get('content-type')))

                if content_type == 'text/html':
                    self.links = self.get_html_links(self.url, self.response.text)

                # Other doc types.
        if not self.links:
            self.links = []
        return self.links



class WebpageBuilder:
    """Builds a Webpage object by intilizing the class and calling
    the `get_page` method.
    """
    @classmethod
    def build(
            cls,
            url,
            user_agent,
            request_kwargs=None,
            respect_robots=True,
            reppy=None):
        """Builds a Webpage by fetching the provided URL.

        Args:
            user_agent (str): The user_agent to use during requests.
                Note: This param overrides any user agent kwargs.
            request_kwargs (dict, optional): The page retrieval request kwargs.
            respect_robots (bool): If true, robots.txt will be honored.
            reppy (:obj:robots.RobotParser, optional): A robots parsing object.
        Returns:
            this: The instance of the Webpage class.

        """
        page = cls._get_page(url, user_agent, request_kwargs, respect_robots, reppy)
        return page

    @classmethod
    def _get_page(
            cls,
            url,
            user_agent,
            request_kwargs=None,
            respect_robots=True,
            reppy=None):
        """Fetches a webpage for the provided URL.

        Args:
            url (str): The url for the webpage.
            user_agent (str): The user_agent to use during requests.
                Note: This param overrides any user agent kwargs.
            request_kwargs (dict, optional): The page retrieval request kwargs.
            respect_robots (bool): If true, robots.txt will be honored.
            reppy (:obj:robots.RobotParser, optional): A robots parsing object.
        Returns:
            Webpage: The instance of the Webpage class.

        """
        webpage = Webpage()
        webpage.url = url
        if not request_kwargs:
            request_kwargs = {}
    	# If headers is already a field in request_kwargs, update with user_agent.
        user_agent_header = {'User-Agent': user_agent}
        if 'headers' in request_kwargs.keys():
            # Update the headers dict to contain the user_agent.
            # If a UA is already specified, `user_agent` param takes precidence.
            request_kwargs['headers'] = {**request_kwargs['headers'], **user_agent_header}
        else:
            request_kwargs['headers'] = user_agent_header

        if respect_robots:
            webpage.allowed_by_robots = webpage.is_allowed_by_robots(
                webpage.url, user_agent, reppy=reppy, request_kwargs=request_kwargs)

        # Only False should prevent crawling (None should allow.)
        if webpage.allowed_by_robots is False:
            webpage.message = f"URL {webpage.url} is restricted by robots.txt"
        else:
            try:
                webpage.response = webpage.fetch(webpage.url, **request_kwargs)
            except Exception as err:
                webpage.message = (
                    "An error occurred while attempting to fetch "
                    f"{webpage.url}: {err}")
                logging.error(webpage.message)
                webpage.error = err
            if webpage.response and not webpage.response.ok:
                webpage.message = f"URL %s returned a {webpage.response.status_code} status code."

        return webpage
