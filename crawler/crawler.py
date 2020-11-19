import requests
import urllib.parse

import link_utils
import parsing
import robots


def _resolve_relative_links(base_url, links):
    links = [
        urllib.parse.urljoin(base_url, link)
        if link_utils.is_relative(link) else link for link in links]
    return links

def _remove_cross_site_links(base_url, links):
    same_site_links = []
    for link in links:
        if link_utils.is_same_host(link, base_url):
            same_site_links.append(link)
    return same_site_links

class Crawler:
    def __init__(
        self, user_agent="python-requests", crawl_delay=None,
        crawl_depth=5, cross_site=False, respect_robots=True,
        requests_kwargs=None):
        self.user_agent = user_agent
        self.crawl_delay = crawl_delay
        self.crawl_depth = crawl_depth
        self.cross_site = cross_site
        self.respect_robots = respect_robots

        if not requests_kwargs:
            self.requests_kwargs = {}
        else:
            self.requests_kwargs = requests_kwargs

    def crawl(self, url):
        original_base_url = link_utils.get_base_url(url)
        crawled_urls = {}
        reppy_robots = {}



print(Crawler(crawl_depth=1).crawl('http://python.org'))
