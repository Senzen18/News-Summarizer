import asyncio
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from typing import List
import asyncio


class TopicExtraction(BaseModel):
    """Extracts topics from news article."""

    topics: List[str] = Field(
        ..., description="A list of topics covered in the news article."
    )


class TopicOverlap(BaseModel):
    """Extracts topics from news article."""

    common_topics: List[str] = Field(
        ..., description="A list of topics covered in the both article."
    )
    unique_topics_1: List[str] = Field(
        ..., description="A list of topics unique to article 1."
    )
    unique_topics_2: List[str] = Field(
        ..., description="A list of topics unique to article 2."
    )


class ComparativeAnalyzer(BaseModel):
    """Compares given pair of articles and extracts comparison and impact."""

    comparison: str = Field(
        ..., description="A sentence of comparative insights between articles."
    )
    impact: str = Field(
        ..., description="A sentence of potential impacts from the compared articles."
    )


class FinalAnalysis(BaseModel):
    """Summarizes the Comparative analysis."""

    english: str = Field(..., description="Summarizes the analysis in english.")
    hindi: str = Field(..., description="Summarizes the analysis in hindi.")


class ChatBot:
    def __init__(
        self, api_key: str, model: str, articles_dict: list, company_name: str
    ):
        self.llm = ChatOpenAI(model=model, api_key=api_key, temperature=0.1)
        articles_list = []
        for i, article in enumerate(articles_dict):
            title = article["title"]
            summary = article["summary"]
            sentiment = article["sentiment"]
            articles_list.append(
                f"title {title} \n summary {summary} \n sentiment {sentiment}  \n\n"
            )

        self.articles = articles_list
        self.company_name = company_name

    async def topic_extraction(self, article: str):
        system_message = """You are an expert in text analysis and topic extraction. Your task is to identify the main topics from a short news articleS.

        ### Instructions:
        - Extract **2 to 3 key topics** that summarize the core ideas of the article.
        - Use **concise, generalizable topics** (e.g., "Electric Vehicles" instead of "Tesla Model X").
        - Avoid generic words like "news" or "report".
        - If relevant, include categories such as **Technology, Finance, Politics, Business, or Science**.
        - Return the topics in **JSON format** as a list of strings.
        - Seperate the topics for each articles by line break.
        - Do not include just he company name {company_name}


        ### Example:

        #### Input Article:
        "Tesla has launched a new AI-powered self-driving feature that improves vehicle autonomy and enhances road safety. The update is expected to impact the automotive industry's shift toward electric and smart vehicles."

        #### Output:
        ["Artificial Intelligence", "Self-Driving Cars", "Automotive Industry", "Electric Vehicles", "Road Safety"]
        :

                        """

        prompt = ChatPromptTemplate.from_messages(
            [("system", system_message), ("human", "Input Article: \n {articles}")]
        )
        structured_llm = self.llm.with_structured_output(TopicExtraction)
        chain = prompt | structured_llm
        response = await chain.ainvoke(
            ({"company_name": self.company_name, "articles": article})
        )
        return response.topics

    async def topic_overlap(self, id1: int, id2: int):
        article_1, article_2 = self.articles[id1], self.articles[id2]

        system_message = """You are an advanced AI specializing in text analysis and topic extraction. Your task is to compare two news articles and extract key topics.

        ### **Instructions:**
        - Identify **common topics** present in **both articles**.
        - Identify **topics unique to each article**.
        - Use **generalized topics** (e.g., "Electric Vehicles" instead of "Tesla Model X").
        - Ensure topics are **concise and meaningful**.
        ---
        ### **Example:**
        #### **Article 1:**
        "Tesla has launched a new AI-powered self-driving feature that enhances vehicle autonomy and road safety. The update is expected to impact the automotive industry."

        #### **Article 2:**
        "Regulators are reviewing Tesla’s self-driving technology due to safety concerns. Experts debate whether AI-based vehicle autonomy meets current legal standards."

        #### **Expected Output:**
        "common_topics": ["Self-Driving Cars", "Artificial Intelligence", "Safety"],
        "unique_topics_1": ["Automotive Industry", "Automotive Industry"],
        "unique_topics_2": ["Regulations", "Legal Standards"]
                        """

        user_message = """
        Here are the news articles on the company.
        Article 1: 
        {article_1} 
        Article 2: 
        {article_2}
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", user_message),
            ]
        )
        structured_llm = self.llm.with_structured_output(TopicOverlap)
        chain = prompt | structured_llm
        response = await chain.ainvoke({"article_1": article_1, "article_2": article_2})
        return {
            "Common Topics ": response.common_topics,
            f"Unique Topics in Article {id1}": response.unique_topics_1,
            f"Unique Topics in Article {id2}": response.unique_topics_2,
        }

    async def comparative_analysis(self, id1: int, id2: int):
        article_1, article_2 = self.articles[id1], self.articles[id2]

        system_message = """
        You are an AI assistant that performs Comparative Analysis on given articles.
        Analyze the following articles and provide a comparative analysis. Highlight their key themes, sentiment, and impact.
        Compare how each article portrays the companies and discuss potential implications for investors and the industry.
        Structure your response with 'Comparison' and 'Impact' sections. 
        The length of each comparison and impact should be less than 20 words
        Mention the articles ids.

        ### **Example:**
        #### **Article 1:**
        ""Tesla's New Model Breaks Sales Records.Tesla's latest EV sees record sales in Q3..."

        #### **Article 2:**
        "Regulatory Scrutiny on Tesla's Self-Driving Tech. Regulators have raised concerns over Tesla’s self-driving software..."

        #### **Expected Output:**
        "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
        "Impact": "The first article boosts confidence in Tesla's market growth, while the second raises concerns about future regulatory hurdles."
        """

        user_message = """
        Here are the news articles on the company.
        Article {id1}: 
        {article_1} 
        Article {id2}: 
        {article_2}
        """

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_message),
                ("human", user_message),
            ]
        )
        structured_llm = self.llm.with_structured_output(ComparativeAnalyzer)
        chain = prompt | structured_llm
        response = await chain.ainvoke(
            {"article_1": article_1, "article_2": article_2, "id1": id1, "id2": id2}
        )
        return {
            f"comparison of {id1}, {id2}": response.comparison,
            "impact": response.impact,
        }

    async def main(self, similar_pairs: list):
        """Runs all OpenAI API calls in parallel."""

        topic_extraction_tasks = [
            self.topic_extraction(article) for article in self.articles
        ]

        topic_overlap_tasks = [
            self.topic_overlap(id1, id2) for id1, id2, _ in similar_pairs
        ]

        comparative_analysis_tasks = [
            self.comparative_analysis(id1, id2) for id1, id2, _ in similar_pairs
        ]

        (
            topic_extraction_results,
            topic_overlap_results,
            comparative_analysis_results,
        ) = await asyncio.gather(
            asyncio.gather(*topic_extraction_tasks),
            asyncio.gather(*topic_overlap_tasks),
            asyncio.gather(*comparative_analysis_tasks),
        )
        return {
            "topic_extraction_results": topic_extraction_results,
            "topic_overlap_results": topic_overlap_results,
            "comparative_analysis_results": comparative_analysis_results,
        }

    def final_analysis(self, comparative_analysis_articles):
        comparative_results = "Comparative Analysis: \n"
        for comparisons in comparative_analysis_articles:
            comparison, impact = comparisons.values()
            comparative_results += f"comparison: {comparison} \n impact: {impact} \n\n"

        template = """
        You are an AI assistant that reads a Comparative Analysis of Articles.
        And summarizes them to produce the final sentiment analysis.
        Make the final sentiment analysis less than 20 words
        Comprative Analysis:
        {comparative_results}
        """
        prompt = ChatPromptTemplate.from_template(template)
        structured_llm = self.llm.with_structured_output(FinalAnalysis)
        chain = prompt | structured_llm
        response = chain.invoke({"comparative_results": comparative_results})
        return response.english, response.hindi
