""" This module provides functionality for crawling the web.

"""
import logging
import time
import concurrent.futures as cf

from . import link_utils
from . import robots
from . import webpage


log = logging.getLogger('bitcrawler')
### Add docs for disabling logging.
# logging.getLogger('bitcrawler').propagate = False



class Crawler:
    """Provides functionality for crawling webpages.

    """
    def __init__(
            self,
            user_agent="python-requests",
            crawl_delay=0,
            crawl_depth=5,
            cross_site=False,
            respect_robots=True,
            respect_robots_crawl_delay=False,
            multithreading=False,
            max_threads=100,
            webpage_builder=webpage.WebpageBuilder,
            request_kwargs=None,
            reppy_cache_capacity=100,
            reppy_cache_policy=None,
            reppy_ttl_policy=None,
            reppy_args=tuple()):
        """ Initializs Crawler.

        Args:
            user_agent (str): The user_agent to use during requests.
                Note: This param overrides any user agent kwargs.
            crawl_delay (int, optional): Seconds to wait between page requests. Default 0.
                Disabled if multithreading is True.
            crawl_depth (bool, optional): Depth of pages to crawl. Default 5.
            cross_site (bool, optional): Allow crawling across domains. Default False.
            respect_robots (bool, optional): Respect robots.txt. Default True.
            respect_robots_crawl_delay (bool, optional): Respect robots.txt crawl delay.
                Disabled if multithreading is True.
            multithreading (bool, optional): Crawl using multithreading. Default False.
            max_threads (int, optional): Max number of treads. Default 100.
                Set to 1 if multithreading is False.
            webpage_class (`obj` webpage.Webpage, optional): The webpage.Webpage class to use
                for fetching and storing relevant webpage info.
                Allows for the extension of the class. Default webpage.Webpage.
            request_kwargs (dict, optional): The page retrieval request kwargs. Default `None`
            reppy_cache_capacity (int, optional): The number of reppy.Robots objects to
                store in cache. Default 100.
            reppy_cache_policy (`obj`, optional): The reppy ttl policy.
                If `None` default is reppy.cache.policy.ReraiseExceptionPolicy(ttl=600).
                See reppy for more details (https://github.com/seomoz/reppy).
            reppy_ttl_policy (`obj`, optional): The reppy ttl policy.
                If `None` default is reppy.Robots.DEFAULT_TTL_POLICY.
                See reppy for more details (https://github.com/seomoz/reppy).
            reppy_args (tuple, optional): Additional args passed to the
                reppy.cache.RobotsCache initialization.

        """
        self.webpage_builder = webpage_builder
        self.user_agent = user_agent
        self.crawl_depth = crawl_depth
        self.cross_site = cross_site
        self.respect_robots = respect_robots
        self.multithreading = multithreading


        if not request_kwargs:
            request_kwargs = {}
    	# If headers is already a field in request_kwargs, update with user_agent.
        user_agent_header = {'User-Agent': user_agent}
        if 'headers' in request_kwargs.keys():
            # Update the headers dict to contain the user_agent.
            # If a UA is already specified, `user_agent` param takes precidence.
            request_kwargs['headers'] = {**request_kwargs['headers'], **user_agent_header}
        else:
            request_kwargs['headers'] = user_agent_header

        self.request_kwargs = request_kwargs
        self.reppy = robots.RobotsCache(
	       reppy_cache_capacity, reppy_cache_policy,
           reppy_ttl_policy, *reppy_args, **self.request_kwargs)

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
        """Parses the webpages. Meant to be Overridden.

        Args:
            webpages (list(webpage.Webpage)): A list of webpages.

        Returns:
            list(webpage.Webpage): The crawled webpages.

        """
        return list(webpages)


    def _wait_crawl_delay(self, url, reppy):
        """Sleeps for the crawl delay.

        Args:
            url (str): The current URL.
            reppy (:obj: `robots.RobotParser`): A reppy object.

        """
        if not self.multithreading:
            if self.respect_robots_crawl_delay:
                robots_crawl_delay = reppy.crawl_delay(url, self.user_agent)
                delay = max(robots_crawl_delay, self.crawl_delay)
            else:
                delay = self.crawl_delay
            time.sleep(delay)


    def _is_crawlable_domain(
        self, url, original_domain, allowed_domains, disallowed_domains):
        """Checks if a domain is crawlable.

        If the domain is the same as the original url, it is crawlable.
        Crawlable if `cross_site` is True and the url domain is in `allowed_domains`.
        Crawlable if `cross_site` is True and the url domain is in `disallowed_domains`.

        Args:
            url (str): The URL to be crawled.
            original_domain (str): The domain from the original URL.
            allowed_domains (list(str)): A list of allowed domains.
                Disabled when `cross_site` is False.
            disallowed_domains (list(str)): A list of disallowed domains.
                Disabled when `cross_site` is False. Disabled when
                allowed domains is not empty/null.

        Returns:
            bool: True if the URL is crawlable. Otherwise False.

        Examples:
            >>> _is_crawlable_domain("http://python.org", "python.org", [], [])
            True

            >>> _is_crawlable_domain("http://python.org", "yahoo.com", ["python.org"], [])
            True

            >>> _is_crawlable_domain("http://python.org", "yahoo.com", [], ["python.org"])
            False

        """
        url_domain = link_utils.LinkUtils.get_domain(url)
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
        """Crawls webpages by traversing links.

        Args:
            url (str): The URL to be crawled.
            allowed_domains (list(str)): A list of allowed domains to crawl. Default None
                Original URL domain takes precidence. `cross_site` must be
                enabled.
            disallowed_domains (list(str)): A list of allowed domains to crawl. Default None.
                Original URL domain takes precidence. `cross_site` must be
                enabled and `allowed_domains` must be empty/null.
            page_timeout (int, optional): Number of seconds to allow for page retrieval. Default 10.

        Returns:
            self.parse(webpages): Returns a call to the overidable parse function.
                Supplies the webpages as input.
        """
        original_domain = link_utils.LinkUtils.get_domain(url)

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
            """"Functionality for crawling a set of urls."""
            # depth starts at 0 so >= terminates
            if depth >= self.crawl_depth:
                return
            futures = []
            with cf.ThreadPoolExecutor(max_workers=self.max_threads) as tpe:
                for url in urls:
                    log.debug("Fetching url %s", url)
                    self._wait_crawl_delay(url, self.reppy)
                    futures.append(
                        tpe.submit(
                            self.webpage_builder.build,
                            url,
                            respect_robots=self.respect_robots,
                            user_agent=self.user_agent,
                            request_kwargs=self.request_kwargs,
                            reppy=self.reppy))

                # Get the results from the concurrent page requests.
                fetched_pages = []
                for index, future in enumerate(futures):
                    try:
                        page = future.result(timeout=page_timeout)
                    except cf.TimeoutError as err:
                        page = webpage.Webpage()
                        page.url = urls[index]
                        page.message = (
                            f"A timeout ({page_timeout} sec) occurred while "
                            f"attempting to fetch url ({page.url})")
                        page.error = err
                        log.error(page.message)
                    except Exception as err:
                        page = webpage.Webpage()
                        page.url = urls[index]
                        page.message = (
                            f"An unexpected error occurred while attempting to "
                            f"fetch url ({page.url}) - {err}")
                        page.error = err
                        log.error(page.message)
                    finally:
                        fetched_pages.append(page)
                        crawled_urls[page.url] = page

                # Get all links from pages that were just fetched.
                links_to_crawl = []
                for page in fetched_pages:
                    page_links = page.get_page_links()
                    valid_links = [
                        link for link in page_links
                        if self._is_crawlable_domain(
                            link, original_domain,
                            allowed_domains,
                            disallowed_domains)]
                    links_to_crawl.extend(valid_links)
                links_to_crawl = list(set(links_to_crawl))

                # crawl links discovered on pages that were just crawled.
                _crawl(links_to_crawl, depth=depth+1)

        _crawl([url])
        return self.parse(crawled_urls.values())
