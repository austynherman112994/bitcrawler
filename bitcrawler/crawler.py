""" TODO
"""
import logging
import time
import concurrent.futures as cf

import link_utils
import robots
import webpage

log = logging.getLogger('bitcrawler').addHandler(logging.NullHandler())
### Add docs for disabling logging.
# logging.getLogger('bitcrawler').propagate = False

class Crawler:
    """TODO: Docstring

    TODOS:
        Add allowed and disallowed domains logic.
        Allowed domains should override cross_site for the povided domains.

        Disallowed domains should only be applied with cross site true.

        ----
        Crawl delays
    """
    def __init__(
            self, user_agent="python-requests",
            crawl_delay=0,
            crawl_depth=5,
            cross_site=False,
            respect_robots=True,
            respect_robots_crawl_delay=False,
            multithreading=False,
            max_threads=100,
            request_kwargs=None,
            reppy_cache_kwargs=None,
            reppy_request_kwargs=None):
        """TODO"""
        self.user_agent = user_agent
        self.crawl_depth = crawl_depth
        self.cross_site = cross_site
        self.respect_robots = respect_robots
        self.request_kwargs = request_kwargs
        self.reppy_cache_kwargs = reppy_cache_kwargs
        self.reppy_request_kwargs = reppy_request_kwargs
        self.multithreading = multithreading

        if multithreading:
            if crawl_delay or respect_robots_crawl_delay:
                log.warning(
                    "Field `crawl_delay` and `respect_robots_crawl_delay` "
                    "are disabled when multithreading is True.")
            self.max_threads = max_threads
        else:
            log.warning(
                "multithreading is set to False. Defaulting "
                "max_threads to 1.")
            self.max_threads = 1
            self.crawl_delay = crawl_delay
            self.respect_robots_crawl_delay = respect_robots_crawl_delay

    def parse(self, webpages):
        """TODO"""
        ### OVERRIDE
        return list(webpages)

    def _crawl_delay(self, url, reppy):
        """TODO"""
        if not self.multithreading:
            if self.respect_robots_crawl_delay:
                robots_crawl_delay = reppy.crawl_delay(url, self.user_agent)
                delay = max(robots_crawl_delay, self.crawl_delay)
            else:
                delay = self.crawl_delay
            time.sleep(delay)


    def _is_crawlable_domain(
        self, url, original_domain, allowed_domains, disallowed_domains):
        """TODO"""
        url_domain = link_utils.get_domain(url)
        if url_domain == original_domain:
            crawlable = True
        elif self.cross_site:
            if allowed_domains:
                crawlable = url in allowed_domains
            elif disallowed_domains:
                crawlable = url not in disallowed_domains
            else:
                crawlable = True
        else:
            crawlable = False

        return crawlable


    def crawl(
        self, url, allowed_domains=None,
        disallowed_domains=None, page_timeout=10):
        """TODO: Docstring

        TODO - ADD multiprocessing.
        TODO - ADD whitelist/blacklist domain logic.
        """
        original_domain = link_utils.get_domain(url)
        reppy = robots.RobotParser(
            cache_kwargs=self.reppy_cache_kwargs,
            request_kwargs=self.reppy_request_kwargs)
        crawled_urls = {}
        if not self.cross_site and (allowed_domains or disallowed_domains):
            log.warning(
                "Fields `allowed_domains` and `disallowed_domains` "
                "are disabled when cross_site is False.")
        if allowed_domains and disallowed_domains:
            log.warning(
                "Fields `allowed_domains` and `disallowed_domains` cannot be "
                "enabled at the same time. `allowed_domains` takes priority.")

        def _crawl(urls, depth=0):
            # depth starts at 0 so >= terminates
            if depth >= self.crawl_depth:
                return
            webpages = [webpage.Webpage(url) for url in urls if url not in crawled_urls.keys()]
            futures = []
            with cf.ThreadPoolExecutor(max_workers=self.max_threads) as tpe:
                for page in webpages:
                    self.crawl_delay(page.url, reppy)
                    futures.append(
                        tpe.submit(
                            page.crawl_page,
                            respect_robots=self.respect_robots,
                            user_agent=self.user_agent,
                            request_kwargs=self.request_kwargs,
                            reppy=reppy))

                # Get the results from the concurrent page requests.
                fetched_pages = []
                for index, future in enumerate(futures):
                    try:
                        page = future.result(timeout=page_timeout)
                    except cf.TimeoutError as err:
                        page = webpages[index]
                        page.message = (
                            f"A timeout ({page_timeout} sec) occurred while "
                            f"attempting to fetch url ({page.url})")
                        page.error = err
                        log.error(page.message)
                    except Exception as err:
                        page = webpages[index]
                        page.message = (
                            f"An unexpected error occurred while attempting to "
                            f"fetch url ({page.url}) - {err}")
                        page.error = err
                        log.error(page.message)
                    finally:
                        fetched_pages.append(page)
                        crawled_urls[page.url] = page

                # Get all links from pages that were just fetched.
                links_to_crawl = set()
                for page in fetched_pages:
                    valid_links = [
                        link
                        for link in page.links
                        if self._is_crawlable_domain(
                            link, original_domain,
                            allowed_domains,
                            disallowed_domains)]
                    links_to_crawl.update(valid_links)
                links_to_crawl = list(links_to_crawl)

                # crawl links discovered on pages that were just crawled.
                _crawl(links_to_crawl, depth=depth+1)

        _crawl([url])
        return self.parse(crawled_urls.values())



crawled_pages = Crawler(
    cross_site=True, crawl_depth=2,
    reppy_request_kwargs={"allow_redirects": False}
).crawl('https://www.yahoo.com')
for pg in crawled_pages:
    if pg.soup:
        print(pg.url, "- ", pg.soup.title)
