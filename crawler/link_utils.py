import urllib.parse


def is_relative(url):
    return not bool(urllib.parse.urlparse(url).netloc)

def get_base_url(url):
    url_obj = urllib.parse.urlparse(url)
    base_url = f"{url_obj.scheme}://{url_obj.netloc}"
    return base_url


def is_same_host(url1, url2):
    return (urllib.parse.urlparse(url1).netloc ==
            urllib.parse.urlparse(url2).netloc)
