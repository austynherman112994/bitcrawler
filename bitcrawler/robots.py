import urllib.parse
from reppy.robots import Robots
from reppy.cache import RobotsCache

import link_utils


class RobotParser:
    def __init__(
            self,
            caching_capacity=100,
            cache_kwargs=None,
            request_kwargs=None):

        if not request_kwargs:
            request_kwargs = {}
        if not cache_kwargs:
            cache_kwargs = {}

        self.request_kwargs = request_kwargs
        self.cache_kwargs = cache_kwargs

        self.reppy = RobotsCache(
            capacity=caching_capacity, **cache_kwargs, **request_kwargs)

    def crawl_delay(self, url, user_agent=""):
        reppy = self.reppy.get(url)
        return reppy.agent(user_agent).delay

    def allowed_by_robots(self, url, user_agent=""):
        return self.reppy.allowed(url, user_agent)
