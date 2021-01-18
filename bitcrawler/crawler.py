"""
"""
import requests
import urllib.parse

import link_utils
import parsing
import robots
import webpage
import logging


class Crawler:
    """TODO: Docstring

    TODOS:
        Add allowed and disallowed domains logic.
        Allowed domains should override cross_site for the povided domains.

        Disallowed domains should only be applied with cross site true.
    """
    def __init__(
            self, user_agent="python-requests",
            crawl_delay=None,
            crawl_depth=5,
            allowed_domains=None,
            disallowed_domains=None,
            cross_site=False,
            respect_robots=True,
            respect_robots_crawl_delay=False,
            multithreading=False,
            max_threads=100,
            request_kwargs=None,
            reppy_cache_kwargs=None,
            reppy_request_kwargs=None):

        self.user_agent = user_agent
        self.crawl_delay = crawl_delay
        self.crawl_depth = crawl_depth
        self.allowed_domains = allowed_domains
        self.disallowed_domains = disallowed_domains
        self.cross_site = cross_site
        self.respect_robots = respect_robots
        self.request_kwargs = request_kwargs
        self.reppy_cache_kwargs = reppy_cache_kwargs
        self.reppy_request_kwargs = reppy_request_kwargs
        if multithreading:
            self.max_threads = max_threads
        else:
            log.warning("multithreading is set to False. Defaulting max_threads to 1.")
            self.max_threads = 1


    def parse(self, webpages):
        ### OVERRIDE
        return list(webpages)



    def crawl(self, url):
        """TODO: Docstring

        TODO - ADD multiprocessing.
        TODO - ADD whitelist/blacklist domain logic.
        """
        reppy = robots.RobotParser(
            cache_kwargs=self.reppy_cache_kwargs,
            request_kwargs=self.reppy_request_kwargs)
        crawled_urls = {}

        def _crawl(urls, depth=0):
            if depth >= self.crawl_depth:
                return
            webpages = [webpage.Webpage(url) if url not in crawled_urls.keys() for url in urls]
            with cf.ThreadPoolExecutor(max_workers=self.max_threads) as e:
                futures = [
                    e.submit(
                        page.crawl_page,
                        respect_robots=self.respect_robots,
                        user_agent=self.user_agent,
                        request_kwargs=self.request_kwargs,
                        reppy=reppy) for page in webpages]

                crawled_urls[url] = page
                if self.cross_site:
                    links = page.links
                else:
                    links = page.same_site_links
                if links:
                    _crawl(links, depth=depth+1)

        _crawl([url])
        return self.parse(crawled_urls.values())



crawled_pages = Crawler(cross_site=True, crawl_depth=2, reppy_request_kwargs={"allow_redirects": False}).crawl('https://www.yahoo.com')
for page in crawled_pages:
    if page.soup:
        print(page.url, "- ", page.soup.title)
