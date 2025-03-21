import gradio as gr
import requests
#from gtts import gTTS
import os
import multiprocessing
import time
import requests
import uvicorn

# FastAPI API URL
API_URL = "http://127.0.0.1:8000"

def run_fastapi():
    os.system("uvicorn api:app --host 127.0.0.1 --port 8000 --reload")

def fetch_news(company_name):
    """Fetch news articles for a given company."""
    response = requests.get(f"{API_URL}/news/{company_name}")
    if response.status_code == 200:
        articles = response.json()["articles"]
        formatted_articles = "\n\n".join([f"Title: {a['title']}\n Summary: {a['summary']}" for a in articles])
        return formatted_articles
    else:
        return "No news found."
    

def analyze_news():
    """Analyze sentiment of previously fetched news."""
    response = requests.get(f"{API_URL}/analyze-news")
    if response.status_code == 200:
        analyzed_articles = response.json()["analyzed_articles"]
        formatted_analysis = "\n\n".join([f"Title: {a['title']}\n Sentiment: {a['sentiment']}" for a in analyzed_articles])
        return formatted_analysis
    else:
        return "Please fetch news first."

def compare_news(api_key, model_name, company_name):
    """Perform comparative news analysis."""
    data = {"api_key": api_key, "model_name": model_name, "company_name": company_name}
    response = requests.post(f"{API_URL}/compare-news", json=data)

    if response.status_code == 200:
        comparison_result = response.json()
        return comparison_result
    else:
        return f"Error: {response.json().get('detail', 'Something went wrong.')}"

def text_to_speech(text):
    """Convert text to speech and return audio file path."""
    if not text.strip():
        return "No text provided.", None
    tts = gTTS(text=text, lang="en")
    audio_path = "news_analysis.mp3"
    tts.save(audio_path)
    return text, audio_path

def run_gradio():
    """Run the improved Gradio UI with better styling."""
    with gr.Blocks(css=".gradio-container {max-width: 700px; margin: auto; text-align: center;}") as demo:
        state = gr.State()
        gr.Markdown("## 📢 Company News & Comparative Analysis App")
        gr.Markdown("Enter a company name, fetch news articles, analyze their sentiment, and compare articles using AI.")

        # Fetch News Section
        with gr.Column():
            gr.Markdown("### 📰 Fetch Company News")
            with gr.Row():

                company_name = gr.Textbox(label="🔍 Company Name", placeholder="e.g., Tesla, Google", scale=3)
                news_button = gr.Button("🚀 Fetch News", scale=1)
            news_output = gr.Textbox(label="News Articles", interactive=False, lines=8)

        # Sentiment Analysis Section
        with gr.Column():
            gr.Markdown("### 📊 Analyze Sentiment")
            analyze_button = gr.Button("📈 Analyze Sentiment")
            sentiment_output = gr.Textbox(label="Sentiment Analysis", interactive=False, lines=6)

        # Comparative Analysis Section
        with gr.Column():
            gr.Markdown("### 🔍 Comparative News Analysis")
            company_input = gr.Textbox(label="🔍 Company Name", placeholder="e.g., Tesla, Google", scale=3)
            api_key_input = gr.Textbox(label="🔑 OpenAI API Key", placeholder="Enter API Key", type="password")
            model_input = gr.Dropdown(
                choices=["gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"], 
                value="gpt-4o-mini", 
                label="🧠 Select AI Model"
            )
            compare_button = gr.Button("🔄 Compare News")
            comparison_output = gr.Textbox(label="Comparative Analysis Result", interactive=False, lines=8)

        # Text-to-Speech Section
        with gr.Column():
            gr.Markdown("### 🎙️ Convert Sentiment Analysis to Speech")
            tts_button = gr.Button("🔊 Convert to Speech")
            audio_output = gr.Audio(label="Audio Output", autoplay=True, scale = 2)

        # Event Handling
        news_button.click(fetch_news, inputs=company_name, outputs=news_output)
        analyze_button.click(analyze_news, outputs=sentiment_output)
        compare_button.click(compare_news, inputs=[api_key_input, model_input, company_input], outputs=comparison_output)
        tts_button.click(text_to_speech, inputs=sentiment_output, outputs=[sentiment_output, audio_output])

    demo.launch() 

if __name__ == "__main__":
    fastapi_process = multiprocessing.Process(target=run_fastapi)
    fastapi_process.start()
    
    time.sleep(3)  
    run_gradio()