import pytest

from bitcrawler import link_utils

def test_is_relative():
    url = "/test/1?some_param=some_val"
    assert True == link_utils.LinkUtils.is_relative(url)

def test_not_is_relative():
    url = "http://python.org"
    assert False == link_utils.LinkUtils.is_relative(url)

def test_get_base_url():
    url = "http://python.org/test/1?some_param=some_val"
    assert "http://python.org" == link_utils.LinkUtils.get_base_url(url)

def test_get_domain():
    url1 = "http://python.org/test/1?some_param=some_val"
    url2 = "http://python.org/search/123"
    url3 = "http://www.test.python.org:8080/abc"
    assert link_utils.LinkUtils.get_domain(url1) == "python.org"
    assert link_utils.LinkUtils.get_domain(url1) == "python.org"
    assert link_utils.LinkUtils.get_domain(url2) == "python.org"

def test_is_same_domain():
    url1 = "http://python.org/test/1?some_param=some_val"
    url2 = "http://python.org/search/123"
    url3 = "http://www.test.python.org:8080"
    assert link_utils.LinkUtils.is_same_domain(url1, url2)
    assert link_utils.LinkUtils.is_same_domain(url1, url3)
    assert link_utils.LinkUtils.is_same_domain(url2, url3)

def test_not_is_same_domain():
    url1 = "http://python.org/test/1?some_param=some_val"
    url2 = "http://pandas.org/search/123"
    assert not link_utils.LinkUtils.is_same_domain(url1, url2)
