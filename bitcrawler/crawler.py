import requests
import urllib.parse

import link_utils
import parsing
import robots
import webpage


class Crawler:
    """TODO: Docstring
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
            for url in urls:
                if url not in crawled_urls.keys():
                    page = webpage.Webpage(url).crawl_page(
                        respect_robots=self.respect_robots,
                        user_agent=self.user_agent,
                        request_kwargs=self.request_kwargs,
                        reppy=reppy
                    )
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
