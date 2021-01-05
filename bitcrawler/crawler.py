import requests
import urllib.parse

from . import link_utils
from . import parsing
from . import robots
from . import webpage


class Crawler:
    def __init__(
            self, user_agent="python-requests",
            crawl_delay=None,
            crawl_depth=5,
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
        self.cross_site = cross_site
        self.respect_robots = respect_robots
        self.request_kwargs = request_kwargs
        self.reppy_cache_kwargs = reppy_cache_kwargs
        self.reppy_request_kwargs = reppy_request_kwargs


    def parse(self, webpages):
        ### OVERRIDE
        results = []
        for page in webpages:
            if page.response:
                status_code = page.response.status_code
            else:
                status_code = None
            if page.soup:
                title = page.soup.title
            else:
                title = None

            results.append({
                'url': page.url,
                'title': title,
                'content_type': page.content_type,
                'status_code': status_code,
                'can_crawl': page.allowed_by_robots,
                # 'links': page.links
            })
        return results



    def crawl(self, url):
        reppy = robots.RobotParser(
            cache_kwargs=self.reppy_cache_kwargs,
            request_kwargs=self.reppy_request_kwargs)

        crawled_urls = {}

        def _crawl_threaded():
            pass

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



for page in Crawler(cross_site=True, crawl_depth=2).crawl('https://www.yahoo.com'):
    print(page)
    print('\n')
