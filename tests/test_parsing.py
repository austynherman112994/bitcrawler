import pytest

from bitcrawler import parsing

def test_get_links():
    result_links = [
        "/about",
        "http://python.org",
        "https://docs.pytest.org/"
    ]
    html = r"""
        <!doctype html>

        <html lang="en">
        <head>
          <meta charset="utf-8">

          <title>The HTML5 Herald</title>
          <meta name="description" content="The HTML5 Herald">
          <meta name="author" content="SitePoint">

          <link rel="stylesheet" href="css/styles.css?v=1.0">

        </head>

        <body>
          <a href="/about">About</a>
          <a href="http://python.org">Python</a>
          <a href="http://python.org">Python</a>
          <a href="https://docs.pytest.org/">Testing</a>
          <script src="js/scripts.js"></script>
        </body>
        </html>
    """
    soup = parsing.HtmlParser(html, "html.parser")
    links = soup.get_links()

    assert links.sort() == result_links.sort()
