from fastapi import FastAPI, HTTPException
from utils import bs4_extractor, SentimentAnalyzer, SemanticGrouping
from llm_utils import *
import openai
import asyncio

app = FastAPI()

# Initialize sentiment analyzer and semantic grouping
sentiment_analyzer = SentimentAnalyzer()
semantic_grouping = SemanticGrouping()



def check_api_key(api_key: str):
    if api_key == None:
        return False
    elif api_key != None:
        client = openai.OpenAI(api_key=api_key)
        try:
            client.models.list()
        except openai.AuthenticationError:
            return False
        else:
            return True
def check_model_name(model_name: str, api_key: str):
  openai.api_key = api_key
  model_list = [model.id for model in openai.models.list()]
  return True if model_name in model_list else False

#Helper function to get articles and article sentiments
def get_articles(company_name: str):
    if not company_name:
        raise HTTPException(status_code=500, detail="The company name is required.")
    
    news_articles = bs4_extractor(company_name)

    if not news_articles:
        raise HTTPException(status_code=500, detail="No news found")

    articles_data = [
            {"title": article["title"], "summary": article["summary"]}
            for article in news_articles
        ]
    
    analyzed_articles = sentiment_analyzer.classify_sentiments(articles_data)

    return news_articles,analyzed_articles

def get_formatted_output(company_name, analyzed_articles, topic_extraction_results,
                        topic_overlap_results,
                        comparative_analysis_results, final_analysis):
    articles = analyzed_articles
    sentiment_distribution = {"positive" : 0, "negative" : 0, "neutral" : 0}
    for i in range(len(articles)):
        articles[i]["topics"] = topic_extraction_results[i]


        sentiment = articles[i]["sentiment"]
        sentiment_distribution[sentiment] += 1
    comparative_sentiment_score = {"Sentiment Distribution" : sentiment_distribution, "Coverage Differences" : comparative_analysis_results, "Topic Overlap" : topic_overlap_results}
    final_output = {"Company" : company_name, "Articles" : articles, "Comparative Sentiment Score" : comparative_sentiment_score, "Final Sentiment Analysis" : final_analysis}

    return final_output


    
@app.get("/news/{company_name}")
def get_news(company_name: str):
    """
    API endpoint to get news for a company.
    Fetches news articles from NYTimes and BBC.
    """
    try:
        news_articles = bs4_extractor(company_name)
        app.state.company_name = company_name
        if not news_articles:
            raise HTTPException(status_code=404, detail="No news found")

        app.state.news_articles = news_articles
        return {"company": company_name, "articles": news_articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/analyze-news")
def analyze_news():
    """
    API endpoint to analyze news articles.
    Performs sentiment analysis on a list of articles.
    """
    if not app.state.news_articles:
        HTTPException(
            status_code=500, detail="Type in the name before the news analysis."
        )
    try:
        articles_data = [
            {"title": article["title"], "summary": article["summary"]}
            for article in app.state.news_articles
        ]
        analyzed_articles = sentiment_analyzer.classify_sentiments(articles_data)
        app.state.articles_with_sentiments = analyzed_articles
        return {"analyzed_articles": analyzed_articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare-news")
async def compare_news(*, api_key: str, model_name: str = "gpt-4o-mini", company_name: str ):
    """
    API endpoint to perform comparative analysis.
    Uses semantic similarity to find the most related articles.
    """
    
    if not check_api_key(api_key):
        HTTPException(
            status_code=500,
            detail="The entered API key does not seem to be right. Please enter a valid API key",
        )

    if not check_model_name(model_name,api_key):
        HTTPException(
            status_code=500,
            detail="The model you specified does not exist.",
        )
    news_articles, analyzed_articles = get_articles(company_name)
    # try:
    articles_text = [
        f"{article['title']}. {article['summary']}"
        for article in news_articles
    ]
    
    if len(articles_text) < 2:
        raise HTTPException(
            status_code=400, detail="At least two articles required for comparison."
        )
    top_similar_articles = semantic_grouping.find_top_k_similar_articles(
        articles_text, k=5
    )

    llm_chatbot = ChatBot(
        api_key,
        model_name,
        analyzed_articles,
        company_name,
    )
    llm_result = await llm_chatbot.main(top_similar_articles)

    (
        topic_extraction_results,
        topic_overlap_results,
        comparative_analysis_results,
    ) = llm_result.values()
    final_analysis = llm_chatbot.final_analysis(comparative_analysis_results)

    final_output = get_formatted_output(company_name, analyzed_articles, topic_extraction_results,
        topic_overlap_results,
        comparative_analysis_results, final_analysis)
    print(final_output)
    return final_output
    
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
