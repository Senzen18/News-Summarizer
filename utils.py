import requests
from bs4 import BeautifulSoup
from transformers import pipeline
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# from transformers import AutoModelForSequenceClassification, AutoTokenizer
import itertools
import re
import heapq
import torch
from gtts import gTTS

def filter_articles(articles_list, company_name):
    """
    Filters articles that only contain the company name.

    Args:
        articles_list (list): List of dictionaries with 'title' and 'summary'.
        company_name (str): The company name to filter articles by.

    Returns:
        list: A filtered list of articles that contain the company name.
    """
    articles_list_filtered = []

    for article in articles_list:
        full_text = (article["title"] + " " + article["summary"]).lower()

        if re.search(company_name.lower(), full_text):
            articles_list_filtered.append(article)

    return articles_list_filtered


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
    articles_list = articles_list[:10]
    articles_filtered = filter_articles(articles_list, company_name)
    return articles_filtered

def save_audio(hindi_text):
    tts = gTTS(text=hindi_text, lang='hi', slow=False)
    tts.save('output.mp3')

class SentimentAnalyzer:

    def __init__(
        self, model_id="mrm8488/deberta-v3-ft-financial-news-sentiment-analysis"
    ):
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.pipe = pipeline(task="text-classification", model=model_id, device=device)

    def classify_sentiments(self, articles_list):
        """
        Classifies the sentiment of each article based on its title and summary.

        Args:
            articles_list (list of dict): A list of articles with 'title' and 'summary' keys.

        Returns:
            list of dict: A new list with added 'sentiment' keys.
        """
        for article in articles_list:
            sentiment = self.pipe(f"{article['title']}. {article['summary']}")
            article["sentiment"] = sentiment[0]["label"]

        return articles_list


class SemanticGrouping:

    def __init__(self, model_id="sentence-transformers/all-MiniLM-L6-v2"):

        self.model = SentenceTransformer(model_id)

    def find_top_k_similar_articles(self, articles, k=5):
        """
        Finds the top-k most similar pairs of articles using cosine similarity.

        Args:
            articles (list of str): A list of article texts to compare.
            k (int, optional): The number of top similar pairs to return. Defaults to 5.

        Returns:
            list of tuples: A list of (index1, index2, similarity_score) tuples.
        """
        embeddings = self.model.encode(articles, convert_to_tensor=True)
        cosine_scores = util.pytorch_cos_sim(embeddings, embeddings)

        pairs = itertools.combinations(range(len(articles)), 2)
        similarity_scores = [(i, j, cosine_scores[i][j].item()) for i, j in pairs]

        top_k_pairs = heapq.nlargest(k, similarity_scores, key=lambda x: x[2])

        return top_k_pairs
