"""Utilities for fetching and parsing robots.txt files.

Extends the reppy library (https://github.com/seomoz/reppy)
for robots.txt fetching and parsing. The utilities below use
the RobotsCache as it is the best suited for a crawling use case.
"""
from reppy.cache import RobotsCache


class RobotParser:
    """RobotsParser leverages the Reppy library for determining robots.txt
    crawling rules and restrictions.

    Attributes:
        reppy (:obj:`reppy.cache.RobotsCache`): The reppy cache object for
            fetching and parsing robots.txt files.

    """
    def __init__(
            self,
            caching_capacity=100,
            cache_kwargs=None,
            request_kwargs=None):
        """ Initializes RobotsParser.

        Args:
            caching_capacity (int, optional): Number of robots objects to cache.
                Default is 100.
            cache_kwargs (dict, optional): kwargs to pass to the reppy cache. Default is None.
            request_kwargs (dict, optional): kwargs to pass to requests.get
                during retrieval of robots.txt. Default is None.
        """

        if not request_kwargs:
            request_kwargs = {}
        if not cache_kwargs:
            cache_kwargs = {}

        self.reppy = RobotsCache(
            capacity=caching_capacity, **cache_kwargs, **request_kwargs)


    def crawl_delay(self, url, user_agent="python-requests"):
        """Gets a crawl delay for a given url and user_agent.

        Note: Crawl delay is the same for all pages under a robots.txt file for
            a given user agent.

        Args:
            url (str): The target URL.
            user_agent (str, optional): The user agent. Default "python-requests"

        Returns:
            int: The number of seconds the specified user_agent should wait between calls.

        Examples:
            >>> crawl_delay("http://python.org", user_agent="python-requests")
            2

        """
        reppy = self.reppy.get(url)
        delay = reppy.agent(user_agent).delay
        if not delay:
            delay = 0
        return delay


    def allowed_by_robots(self, url, user_agent="python-requests"):
        """Determines if a url is crawlable by the specified user agent.

        Args:
            url (str): The target URL.
            user_agent (str, optional): The user agent. Default "python-requests"

        Returns:
            bool: True if crawling is allowed by robots.txt. Otherwise False.

        Examples:
            >>> allowed_by_robots("http://python.org", user_agent="python-requests")
            True

        """
        return self.reppy.allowed(url, user_agent)
