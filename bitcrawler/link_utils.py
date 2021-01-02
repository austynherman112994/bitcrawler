import urllib.parse


def is_relative(url):
    return not bool(urllib.parse.urlparse(url).netloc)

def get_base_url(url):
    url_obj = urllib.parse.urlparse(url)
    base_url = f"{url_obj.scheme}://{url_obj.netloc}"
    return base_url

def is_same_domain(url1, url2):
    url1_netloc = urllib.parse.urlparse(url1).netloc
    url2_netloc = urllib.parse.urlparse(url2).netloc
    url1_domain = ".".join(url1_netloc.netloc.split(".")[-2:]).split(":")[0]
    url2_domain = ".".join(url2_netloc.netloc.split(".")[-2:]).split(":")[0]
    return url1_domain == url2_domain
