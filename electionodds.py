"""electionodds.py

Python library that fetches and parses election betting odds.
"""

import requests
from lxml.html import fromstring

URL = "https://electionbettingodds.com/"
"""The URL to fetch from"""


class ScraperError(Exception):
    """Exception raised if something in the scraping process fails.
    """


def _parse_odd(col1, col2):
    """Parse one column's row of odds from a page.

    Args:
        col1: The first column (has the image/name)
        col2: The second column (has the percentage)

    Returns:
        A tuple of the candidate name and odds, or None and None if not found
    """

    imgs = col1.cssselect("img")

    if len(imgs) > 0:
        # Strip off the / and extension
        name = imgs[0].get("src")[1:-4]
    else:
        name = None

    ps = col2.cssselect("p")

    if len(ps) > 0 and ps[0].text is not None:
        # Strip off the %
        odds = float(ps[0].text[:-1])
    else:
        odds = None

    return name, odds


def _scrape_odds(document):
    """Return a generator for democratic, republican, and presidential odds
    rows.

    Args:
        document: The HTML document

    Returns:
        A generator of 3-tuples of 2-tuples of candidate names and odds,
        for democratic, republican, and presidential odds.
    """

    # Get the relevant table rows
    for row in document.cssselect(".auto-style4 tr"):
        cols = row.cssselect("td")

        d_info = _parse_odd(cols[0], cols[1])
        r_info = _parse_odd(cols[2], cols[3])
        p_info = _parse_odd(cols[4], cols[5])

        yield d_info, r_info, p_info


def _fetch_page(url):
    """Fetch the page and yield a HTML doc.

    Args:
        url (str): The URL

    Returns:
        A lxml HTML document
    """

    resp = requests.get(url)

    html_doc = fromstring(resp.text)
    return html_doc


def get_odds():
    """Get the democratic, republican, and presidential race odds.

    Returns:
        A 3-tuple of the odds for the democratic, republican,
        and presidential race odds. Each item is a dict mapping candidate
        names to their odds.
    """

    doc = _fetch_page(URL)

    d_odds = {}
    r_odds = {}
    p_odds = {}

    try:
        for (d_name, d_odd), (r_name, r_odd), (p_name, p_odd) in _scrape_odds(
                doc):
            if d_name is not None:
                d_odds[d_name] = d_odd
            if r_name is not None:
                r_odds[r_name] = r_odd
            if p_name is not None:
                p_odds[p_name] = p_odd

        return d_odds, r_odds, p_odds
    except (IndexError, ValueError, TypeError, AttributeError):
        raise ScraperError("Could not parse the page")
