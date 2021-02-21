# BitCrawler
## What is it?
**Bitcrawler** is a Python package that provides functionality for crawling & scraping the web. The library brings simplicity, speed, and extensibility to any crawling project.
The library can be exteded to easily add on additional crawling behavior and functionality for specific use cases.


## Installation
```sh
pip install bitcrawler
```

## Documentation

See the documentation at https://bitcrawler.readthedocs.io/en/latest/bitcrawler.html#bitcrawler for more details on usage.

## Example Crawler
The below example extends the crawler object and overrides the parse function.
The parse function is always called at the end of crawling. It is passed all the pages fetched.
In the below example the pages are parsed using beautifulsoup and the title is printed with the URL.
```py
from bs4 import BeautifulSoup
from bitcrawler.crawler import Crawler

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
crawler = MyCrawler(cross_site=True, crawl_depth=2, multithreading=True)
# Crawls pages starting from "http://test.com"
crawled_pages = crawler.crawl("http://test.com")
```
