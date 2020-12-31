from bs4 import BeautifulSoup

class HtmlParser(BeautifulSoup):
    def get_links(self):
        return list(set(a['href'] for a in self.find_all('a', href=True)))
