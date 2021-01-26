# -*- coding: utf-8 -*-
"""Utilities for parsing html.

Extends functionality of BeautifulSoup for added html parsing functionality.

"""
from bs4 import BeautifulSoup


class HtmlParser(BeautifulSoup):
    """HtmlParser extends functionality provided by BeautifulSoup."""

    def get_links(self):
        """Finds links from anchor tags in the soup.

        Args:
            None

        Returns:
            list(str): A list of links discovered within the html.

        Examples:
            >>> response = requests.get("http://python.org")
            >>> HtmlParser(response.text).get_links()
            ["http://python.org/search", "/about", ..., "http://python.org/learn"]

        """
        return list(set(a["href"] for a in self.find_all("a", href=True)))
