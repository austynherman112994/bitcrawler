"""Utilities for fetching and parsing robots.txt files.

Extends the reppy library (https://github.com/seomoz/reppy)
for robots.txt fetching and parsing.

"""

import urllib.parse
import reppy.cache
from reppy.robots import Robots
from . import link_utils


class RobotsCache(reppy.cache.RobotsCache):
    """Extends the reppy RobotsCache to include extra functionality.

    """

    def crawl_delay(self, url, user_agent="python-requests"):
        """Gets a crawl delay for a given url and user_agent.
        Note: Crawl delay is the same for all pages under a robots.txt file for
            a given user agent.
        Note: Going to open a PR on reppy to have this built in.
        Args:
            url (str): The target URL.
            user_agent (str, optional): The user agent. Default "python-requests"
        Returns:
            int: The number of seconds the specified user_agent should wait between calls.
        Examples:
            >>> crawl_delay("http://python.org", user_agent="python-requests")
            2
        """
        robots = self.get(url)
        delay = robots.agent(user_agent).delay
        if not delay:
            delay = 0
        return delay


class ReppyUtils:
    """A set of reppy utilities.
    """
    @classmethod
    def get_robots_url(cls, url):
        """ Gets the URL where the robots file should be stored.

        Args:
            url (str): The url to derive the robots url from.

        Returns:
            str: The robots.txt url.

        Examples:
            >>> ReppyUtils.get_robots_url('http://python.org/test/path")
            'http://python.org/robots.txt'_
        """
        base_url = link_utils.LinkUtils.get_base_url(url)
        robots_url = urllib.parse.urljoin(base_url, "robots.txt")
        print(robots_url)
        return robots_url

    @classmethod
    def fetch_robots(cls, robots_url, request_kwargs=None):
        """Fetches the robots URL.

        Args:
            robots_url (str): The robots url to fetch.
            requests_kwargs (dict, optional): The keyword arguments to pass into
                the requests.get call to the robots.txt url. Default `None`
        Returns:
            reppy.Robots: the reppy object from feting the robots.txt file.
        """
        if not request_kwargs:
            request_kwargs = {}
        robots = Robots.fetch(robots_url, **request_kwargs)
        return robots

    @classmethod
    def crawl_delay(cls, url, user_agent, request_kwargs=None):
        """Determines the robots crawl delay for a given user agent.

        Args:
            url (str): The url to get a crawl delay for.
            user_agent: The user agent to get the crawl delay for.
            requests_kwargs (dict, optional): The keyword arguments to pass into
                the requests.get call to the robots.txt url. Default `None`

        Returns:
            int: The time to wait between crawling pages (seconds).

        Examples:
            >>> ReppyUtils.crawl_delay('http://python.org/test', 'python-requests')
            2
        """
        if not request_kwargs:
            request_kwargs = {}
        robots_url = cls.get_robots_url(url)
        robots = cls.fetch_robots(robots_url, **request_kwargs)
        return robots.agent(user_agent).delay

    @classmethod
    def allowed(cls, url, user_agent="python-requests", request_kwargs=None):
        """Determines if a URL is crawlable for a given user agent.

        Args:
            url (str): The url to check for crawlability.
            user_agent (str, optional): The user agent to check for in robots.txt.
                Default 'python-requests'.
            requests_kwargs (dict, optional): The keyword arguments to pass into
                the requests.get call to the robots.txt url. Default `None`

        Returns:
            bool: True if the page is allowed to be crawled.

        Examples:
            >>> ReppyUtils.allowed('http://python.org/test')
            True

        """
        if not request_kwargs:
            request_kwargs = {}
        robots_url = cls.get_robots_url(url)
        robots = cls.fetch_robots(robots_url, **request_kwargs)
        return robots.allowed(url, user_agent)
