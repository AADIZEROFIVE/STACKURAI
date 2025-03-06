from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv(".env")
NEWS_API_KEY = os.getenv("NEWSD_API_KEY")  # NewsData.io API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Google Gemini API Key

if not NEWS_API_KEY or not GEMINI_API_KEY:
    raise ValueError("Missing API keys in .env file")

# Initialize Gemini API
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.5,
    timeout=60
)

# Initialize FastAPI app
app = FastAPI(title="News Summarizer Chatbot")

# Define request body model
class NewsRequest(BaseModel):
    topic: str
    location: str = "India"  # Default location
    profession: str = "General"  # Default to general news

# Function to fetch news from NewsData.io
def fetch_news(topic: str, location: str) -> str:
    url = f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q={topic}&country={location}&language=en"
    response = requests.get(url)

    print("Response Status Code:", response.status_code)
    print("Response Content:", response.text)  # Print full response for debugging

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch news")

    articles = response.json().get("results", [])
    if not articles:
        return "No relevant news articles found."

    return "\n".join([f"{idx}. {a['title']}" for idx, a in enumerate(articles[:3], 1)])
    url = f"https://newsdata.io/api/1/latest?apikey={NEWS_API_KEY}&q={topic}&country={location}&language=en"
    response = requests.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch news")

    articles = response.json().get("results", [])
    if not articles:
        return "No relevant news articles found."

    # Select the top 3 latest news articles
    top_articles = articles[:3]
    news_content = ""
    for idx, article in enumerate(top_articles, start=1):
        news_content += f"{idx}. **{article['title']}**\n{article['description']}\n[Read More]({article['link']})\n\n"

    return news_content

# Function to summarize news using Gemini
def summarize_news(news: str, profession: str) -> str:
    try:
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"Summarize the news for a {profession}. Keep it short and relevant."),
            ("human", "{news_content}")
        ])

        prompt = prompt_template.format_messages(news_content=news)
        response = llm.invoke(prompt)

        if response and response.content:
            return response.content
        else:
            return "Failed to summarize news. Please try again later."

    except Exception as e:
        print("Gemini API Error:", str(e))
        return "Error: Unable to generate summary."
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"You are an AI assistant that summarizes news based on a person's profession. Summarize the news for someone who is a {profession}. Keep it short, factual, and relevant."),
        ("human", "{news_content}")
    ])

    prompt = prompt_template.format_messages(news_content=news)
    response = llm.invoke(prompt)

    return response.content if response else "Failed to summarize news."

# Define chatbot API endpoint
@app.post("/news")
async def get_news(request: NewsRequest):
    try:
        # Fetch raw news
        raw_news = fetch_news(request.topic, request.location)

        # Summarize news based on profession
        summarized_news = summarize_news(raw_news, request.profession)

        return {"topic": request.topic, "location": request.location, "news_summary": summarized_news}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.84.150", port=8000)
