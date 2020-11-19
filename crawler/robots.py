import urllib.parse
from reppy.robots import Robots

import link_utils

class RobotParser:
    def __init__(self, url, request_kwargs=None):
        if not request_kwargs:
            request_kwargs = {}
        self.robots_url = self.get_robots_url(url)
        self.reppy = self.fetch_robots(self.robots_url, **request_kwargs)

    @classmethod
    def get_robots_url(cls, url):
        base_url = link_utils.get_base_url(url)
        robots_url = urllib.parse.urljoin(base_url, "robots.txt")
        print(robots_url)
        return robots_url

    @classmethod
    def fetch_robots(cls, robots_url, request_kwargs=None):
        if not request_kwargs:
            request_kwargs = {}
        robots = Robots.fetch(robots_url, **request_kwargs)
        return robots

    def crawl_delay(self, user_agent):
        return self.reppy.agent(user_agent).delay

    def allowed_by_robots(self, url, user_agent=""):
        return self.reppy.allowed(url, user_agent)
