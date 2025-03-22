# News Summarization and Text-to-Speech Application

## Overview
This project is a web-based application that extracts key details from multiple news articles related to a given company, performs sentiment analysis, conducts a comparative analysis, and generates a text-to-speech (TTS) output in Hindi.

## Features
- **News Extraction**: Scrapes and displays at least 10 news articles from The New York Times and BBC.
- **Sentiment Analysis**: Categorizes articles into Positive, Negative, or Neutral sentiments.
- **Comparative Analysis**: Groups articles with most semantic similarity. Then compares the groups to derive insights on how a company's news coverage varies.
- **Text-to-Speech (TTS)**: Converts the summarized sentiment report into Hindi speech.
- **User Interface**: Provides a simple web-based interface using Gradio.
- **API Integration**: Implements FastAPI for backend communication.
- **Deployment**: Deployable on Hugging Face Spaces.

## Tech Stack
- **Frontend**: Gradio
- **Backend**: FastAPI
- **Scraping**: BeautifulSoup
- **NLP**: OpenAI GPT models, LangChain, Sentence Transformers
- **Sentiment Analysis**: Pre-trained Transformer model
- **Text-to-Speech**: Google TTS (gTTS)
- **Deployment**: Uvicorn, Hugging Face Spaces

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Senzen18/News-Summarizer.git
cd News-Summarizer
```

### 2. Install Dependencies
Ensure you have Python 3.8+ installed. Then, run:
```bash
pip install -r requirements.txt
```

### 3. To run Fast API endpoints
Start the FastAPI backend:
```bash
uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

### 4. To run the both Gradio and Fast API
Start the FastAPI backend:
```bash
gradio app.py
```

### 5. Access the Application
Once started, access the Gradio UI at:
```
http://127.0.0.1:7860
```

---

## API Endpoints

### 1. Fetch News
**GET** `/news/{company_name}`
- Fetches the latest articles related to a company.
- **Example:** `/news/Tesla`

### 2. Analyze News Sentiment
**GET** `/analyze-news`
- Performs sentiment analysis on the extracted articles.

### 3. Compare News Articles
**POST** `/compare-news`
- Performs comparative analysis.
- **Request Body:**
```json
{
  "api_key": "your-openai-api-key",
  "model_name": "gpt-4o-mini",
  "company_name": "Tesla"
}
```

### 4. Generate Hindi Summary 
**GET** `/hindi-summary`
- Returns the summarized analysis in Hindi and stores the speech file.

---

## File Structure
```
├── api.py               # FastAPI backend for news extraction, sentiment analysis, and comparison
├── app.py               # Gradio frontend to interact with users
├── llm_utils.py         # Handles OpenAI API calls for topic extraction and comparative analysis
├── utils.py             # Utility functions for web scraping, sentiment analysis, and TTS
├── requirements.txt     # Dependencies
└── README.md            # Project documentation
```

---

## Assumptions and Limitations
- Only extracts articles from The New York Times and BBC.
- Requires a valid OpenAI API key for sentiment analysis and comparison.
- Hindi speech output uses gTTS, which requires an internet connection.

---

## Deployment
This project can be deployed on Hugging Face Spaces. To deploy:
1. Push your repository to GitHub.
2. Follow [Hugging Face Spaces documentation](https://huggingface.co/docs/spaces) for deployment.

---

## Example Output
```json
{
  "Company": "Tesla",
  "Articles": [
    {
      "Title": "Tesla's New Model Breaks Sales Records",
      "Summary": "Tesla's latest EV sees record sales in Q3...",
      "Sentiment": "Positive",
      "Topics": ["Electric Vehicles", "Stock Market", "Innovation"]
    }
  ],
  "Comparative Sentiment Score": {
    "Sentiment Distribution": {"Positive": 1, "Negative": 1, "Neutral": 0},
    "Coverage Differences": [{
      "Comparison": "Article 1 highlights Tesla's strong sales, while Article 2 discusses regulatory issues.",
      "Impact": "Investors may react positively to growth news but stay cautious due to regulatory scrutiny."
    }],
    "Topic Overlap": {
      "Common Topics": ["Electric Vehicles"],
      "Unique Topics in Article 1": ["Stock Market", "Innovation"],
      "Unique Topics in Article 2": ["Regulations", "Autonomous Vehicles"]
    }
  },
  "Final Sentiment Analysis": "Tesla’s latest news coverage is mostly positive. Potential stock growth expected.",
  "Audio": "[Play Hindi Speech]"
}
```

---

## Contributing
Feel free to contribute by:
- Adding more news sources
- Improving the sentiment model
- Enhancing the UI

---

## Contact
For queries, reach out at [your-email@example.com].

