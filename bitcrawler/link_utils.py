# -*- coding: utf-8 -*-
"""Provides tools for interacting with links and URLs.

"""
import urllib.parse


class LinkUtils:
    """Utils for working with URLs and links."""
    @classmethod
    def is_relative(cls, link):
        """Determines if a link is a relative link.

        Args:
            link (str): A link.

        Returns:
            bool: True if the link is a relative link. Otherwise False.

        Examples:
            >>> is_relative("/test/link/path")
            True

            >>> is_relative("http://python.org/test/link/path")
            False

        """
        return not bool(urllib.parse.urlparse(link).netloc)

    @classmethod
    def get_base_url(cls, url):
        """Gets the base url (scheme://netloc) from a url.

        Uses the python urllib.parse object to generate the scheme and netloc.

        Args:
            url (str): A URL.

        Returns:
            string: The base url generated from the provided url.

        Examples:
            >>> get_base_url("http://python.org:8000/test/link/path")
            "http://python.org:8000"

        """
        url_obj = urllib.parse.urlparse(url)
        base_url = f"{url_obj.scheme}://{url_obj.netloc}"
        return base_url

    @classmethod
    def get_domain(cls, url):
        """Checks is two urls share the same domain.

        Generates domains from the urllib.parse objects netloc. The domain is
        extracted from the netloc by stripping the port and subdomain info.

        Args:
            url (str): A URL.

        Returns:
            str: The domain of from the input URL.

        Examples:
            >>> get_domain("http://subdomain.python.org:8000/test/link/path")
            "python.org"

        """
        url_netloc = urllib.parse.urlparse(url).netloc
        url_domain = ".".join(url_netloc.split(".")[-2:]).split(":")[0]
        return url_domain

    @classmethod
    def is_same_domain(cls, url1, url2):
        """Checks is two urls share the same domain.

        Uses `get_domain` to extract a domain.

        Args:
            url1 (str): The first URL for comparison.
            url2 (str): The second URL for comparison.

        Returns:
            bool: True if the domains match. Otherwise False.

        Examples:

            >>>is_same_domain("http://python.org", "https://subdomain.python.org:8000")
            True

            >>>is_same_domain("http://python.org", "https://pandas.com")
            False

        """
        return cls.get_domain(url1) == cls.get_domain(url2)
