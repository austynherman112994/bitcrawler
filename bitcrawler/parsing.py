"""TODO: Docstring
"""
from bs4 import BeautifulSoup

class HtmlParser(BeautifulSoup):
    """TODO: Docstring
    """
    def get_links(self):
        """TODO: Docstring
        """
        return list(set(a['href'] for a in self.find_all('a', href=True)))
