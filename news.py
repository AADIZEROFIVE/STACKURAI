from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import os
import logging
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env")
NEWS_API_KEY = os.getenv("NEWSD_API_KEY")  # NewsData.io API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Google Gemini API Key

# Validate API keys
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define request body model
class NewsRequest(BaseModel):
    topic: str
    location: str = "in"  # ISO country code for India
    profession: str = "General"  # Default to general news

# Define a more detailed Article model
class Article(BaseModel):
    title: str
    description: Optional[str] = None
    link: Optional[str] = None
    source_id: Optional[str] = None
    published_at: Optional[str] = None

# Function to fetch news from NewsData.io with more detailed parsing
def fetch_news(topic: str, location: str) -> List[Article]:
    try:
        url = "https://newsdata.io/api/1/latest"
        params = {
            "apikey": NEWS_API_KEY,
            "q": topic,
            "country": location,
            "language": "en"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        raw_articles = data.get("results", [])
        
        # Convert raw articles to Article models
        articles = []
        for article in raw_articles[:5]:  # Increased to 5 articles
            articles.append(Article(
                title=article.get('title', 'Untitled'),
                description=article.get('description', 'No description'),
                link=article.get('link'),
                source_id=article.get('source_id', 'Unknown'),
                published_at=article.get('pubDate')
            ))
        
        return articles
    
    except requests.RequestException as e:
        logger.error(f"News API request failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch news: {str(e)}")

# Function to summarize news using Gemini
def summarize_news(articles: List[Article], profession: str, topic: str) -> str:
    try:
        # Prepare news content for summarization
        news_content = "\n\n".join([
            f"Title: {article.title}\n"
            f"Description: {article.description}\n"
            f"Source: {article.source_id}"
            for article in articles
        ])

        # More detailed prompt for summarization
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are an advanced AI news summarizer. 
            Provide a comprehensive yet concise summary of the latest news about {topic}.
            
            Target Audience Perspective: {profession}
            
            Summary Guidelines:
            - Synthesize key points from multiple news sources
            - Provide context and potential implications
            - Maintain objectivity and clarity
            - Use professional, informative language
            - Aim for 4-5 sentences maximum
            """),
            ("human", "{news_content}")
        ])

        prompt = prompt_template.format_messages(news_content=news_content)
        response = llm.invoke(prompt)

        return response.content if response else "Unable to generate a summary."
    
    except Exception as e:
        logger.error(f"News summarization error: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# Define main news endpoint
@app.post("/news")
async def get_news(request: NewsRequest):
    try:
        # Fetch news articles
        news_articles = fetch_news(request.topic, request.location)

        # If no articles found
        if not news_articles:
            raise HTTPException(status_code=404, detail="No news articles found for the given topic and location")

        # Summarize news
        summarized_news = summarize_news(
            news_articles, 
            request.profession, 
            request.topic
        )

        return {
            "topic": request.topic,
            "location": request.location,
            "profession": request.profession,
            "articles": [article.dict() for article in news_articles],
            "news_summary": summarized_news
        }

    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "news_api": bool(NEWS_API_KEY),
        "gemini_api": bool(GEMINI_API_KEY)
    }

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.113", port=8000)