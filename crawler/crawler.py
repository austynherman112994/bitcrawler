import requests
import urllib.parse

import link_utils
import parsing
import robots


class Crawler:
    def __init__(
            self, user_agent="python-requests", crawl_delay=None,
            crawl_depth=5, cross_site=False, respect_robots=True,
            requests_kwargs=None, robots_cache_kwargs=None,
            robots_request_kwargs=None):
        self.user_agent = user_agent
        self.crawl_delay = crawl_delay
        self.crawl_depth = crawl_depth
        self.cross_site = cross_site
        self.respect_robots = respect_robots
        self.requests_kwargs = requests_kwargs
        self.robots_cache_kwargs = robots_cache_kwargs
        self.robots_request_kwargs = robots_request_kwargs

    def crawl(self, url):
        reppy = RobotParser(
            cache_kwargs=self.reppy_cache_kwargs,
            request_kwargs=self.reppy_robots_kwargs)
        crawled_urls = {}




print(Crawler(crawl_depth=1).crawl('http://python.org'))
