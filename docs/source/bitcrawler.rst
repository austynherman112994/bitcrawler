bitcrawler
==========
**What is it?**

*Bitcrawler* is a Python package that provides functionality for crawling & scraping the web. The library brings simplicity, speed, and extensibility to any crawling project.
The library can be exteded to easily add on additional crawling behavior and functionality for specific use cases.


**Installation**

.. code-block:: sh

    pip install bitcrawler


**Dependencies**

- Reppy
- BeautifulSoup4
- Requests


**Example Crawler**

*Simple Usage*

.. code-block:: python
    
    from bitcrawler.crawler import Crawler

    crawler = Crawler()
    crawled_pages = crawler.crawl('http://test.com')


*Advanced Usage*

The below example extends the crawler object and overrides the parse function.
The parse function is always called at the end of crawling. It is passed all the pages fetched.
In the below example the pages are parsed using beautifulsoup and the title is printed with the URL.

.. code-block:: python

    from bs4 import BeautifulSoup
    from bitcrawler.crawler import Crawler
    from bitcrawler import webpage

    class MyCrawler(Crawler):
        # Parse is always called py the `crawl` method and is provided
        # a webpage.Webpage class instance for each URL.
        # See the webpage.Webpage class for details about the object.
        def parse(self, webpages):
            for page in webpages:
                # If page response is not none, response code is in 200s, and document is html.
                if page.response and \
                   page.response.ok and \
                   page.response.headers.get('content-type').startswith('text/html'):
                    soup = BeautifulSoup(page.response.text, "html.parser")
                    print(page.url, "- ", soup.title) 
            return webpages

    # Initializes the crawler with the configuration specified by parameters.
    crawler = MyCrawler(
        user_agent='python-requests', # The User Agent to use for all requests.
        crawl_delay=0, # Number of seconds to wait between web requests.
        crawl_depth=2, # The max depth from following links (Default is 5).
        cross_site=False, # If true, domains other than the original domain can be crawled.
        respect_robots=True, # If true, the robots.txt standard will be followed.
        respect_robots_crawl_delay=True, # If true, the robots.txt crawl delay will be followed.
        multithreading=True, # If true, parallelizes requests for faster crawling.
        max_threads=100, # If multithreading is true, this determines the number of threads.
        webpage_builder=webpage.WebpageBuilder, # Advanced Usage - Allows the WebpageBuilder class to be overridden to allow modificaion.
        request_kwargs={'timeout': 10}, # Additional keyword arguments that you would like to pass into any request made.
        reppy_cache_capacity=100, # The number of robots.txt objects to cache. Eliminates the need to fetch robots.txt file many times.
        reppy_cache_policy=None, # Advanced Usage - See docs for details.
        reppy_ttl_policy=None, # Advanced Usage - See docs for details.
        reppy_args=tuple()) # Advanced Usage - See docs for details.
 
    # Crawls pages starting from "http://test.com"
    crawled_pages = crawler.crawl(
        url="http://test.com", # The start URL to crawl from.
        allowed_domains=[], # A list of allowed domains. `cross_site` must be True. Ex. ['python.org',...]
        disallowed_domains=[], # A list of disallowed domains. `cross_site` must be True and `allowed_domains` empty.
        page_timeout=10) # The ammount of time before a page retrieval/build times out.
 


Submodules
----------

bitcrawler.crawler module
-------------------------

.. automodule:: bitcrawler.crawler
   :members:
   :undoc-members:
   :show-inheritance:

bitcrawler.link\_utils module
-----------------------------

.. automodule:: bitcrawler.link_utils
   :members:
   :undoc-members:
   :show-inheritance:

bitcrawler.parsing module
-------------------------

.. automodule:: bitcrawler.parsing
   :members:
   :undoc-members:
   :show-inheritance:

bitcrawler.robots module
------------------------

.. automodule:: bitcrawler.robots
   :members:
   :undoc-members:
   :show-inheritance:

bitcrawler.webpage module
-------------------------

.. automodule:: bitcrawler.webpage
   :members:
   :undoc-members:
   :show-inheritance:

Module contents
---------------

.. automodule:: bitcrawler
   :members:
   :undoc-members:
   :show-inheritance:
