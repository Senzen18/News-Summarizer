import requests
from bs4 import BeautifulSoup
import pandas as pd


def bs4_extractor(company_name: str):
    """
    Extracts news articles from The New York Times and BBC for a given company.

    Args:
        company_name (str): The name of the company to search for.

    Returns:
        list: A list of dictionaries containing article titles and summaries.
    """
    articles_list = []

    # Fetch and parse NYTimes articles
    nytimes_url = f"https://www.nytimes.com/search?query={company_name}"
    nytimes_page = requests.get(nytimes_url).text
    nytimes_soup = BeautifulSoup(nytimes_page, "html.parser")

    for article in nytimes_soup.find_all("li", {"data-testid": "search-bodega-result"}):
        try:
            title = article.find("h4").text.strip()
            summary = article.find("p", {"class": "css-e5tzus"}).text.strip()

            if not title or not summary:
                continue

            articles_list.append({"title": title, "summary": summary})
        except AttributeError as e:
            print(f"NYTimes Extraction Error: {e}")
            continue

    # Fetch and parse BBC articles
    bbc_url = f"https://www.bbc.com/search?q={company_name}"
    bbc_page = requests.get(bbc_url).text
    bbc_soup = BeautifulSoup(bbc_page, "html.parser")

    for article in bbc_soup.find_all("div", {"data-testid": "newport-article"}):
        try:
            title = article.find("h2", {"data-testid": "card-headline"}).text.strip()
            summary = article.find(
                "div", {"class": "sc-4ea10043-3 kMizuB"}
            ).text.strip()

            if not title or not summary:
                continue

            articles_list.append({"title": title, "summary": summary})
        except AttributeError as e:
            print(f"BBC Extraction Error: {e}")
            continue

    return articles_list
