from django.shortcuts import render
import json
from django.http import JsonResponse, HttpResponseServerError
from django.conf import settings
import os
import logging
import traceback
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

# Load environment variables
load_dotenv("../.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Check if API key is available
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

logger = logging.getLogger(__name__)

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    temperature=0,
    timeout=60,
    max_retries=2
)

# Define a prompt template for the chatbot
constitution_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are a knowledgeable assistant specializing in the Indian Constitution.
      Provide accurate and easy-to-understand explanations about fundamental rights, duties, legal provisions, and citizen responsibilities.
      Make sure to consider interaction whith people with very basic knowledge as there are from remote areas.
      help them with legal advice. Tell them steps to take when they ask any how to related questions.
      You should be able to communicate in all local languages of mainly India also others.   
      Understand the user's legal issue criminal, civil, property, family law, etc.
      Provide step-by-step guidance on filing complaints, understanding rights, and legal processes.
      Suggest relevant constitutional articles and laws applicable to their situation.
      Offer information on legal aid services and government schemes.
      Ensure accessibility by simplifying complex legal jargon.     
      Be on point and give whats the neccesity only if the user asks for it.
      IMPORTANT: Provide relevant government link for the solution
     """),
    ("human", "{user_input}")
])

govt_prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an assistant providing information on government subsidies and benefits.
      respond with a numbered list of available schemes and their short descriptions.
      let the values and steps be on top and explanation later.
      Do not add extra explanations, greetings, or unrelated information.
      include msp's and other related information. Be on point and give values when asked about prices.
     """),
    ("human", "{user_input}")
])

@login_required(login_url='/authentication/login/')
def constitution_chatbot_view(request):
    """
    Render the main chatbot interface
    """
    return render(request, 'chatbot/const_index.html')

def constitution_process_chat(request):
    """
    Process chat messages using the LLM directly
    """
    if request.method == 'POST':
        try:
            # Get the user message from the POST request
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
            
            # Check if the input is empty
            if not user_input.strip():
                return JsonResponse({'error': 'Please enter a message'}, status=400)
            
            # Create the prompt with user input
            prompt = constitution_prompt_template.format_messages(user_input=user_input)
            # Call the LLM directly
            response = llm.invoke(prompt)
            # Return the response
            return JsonResponse({'response': response.content})
                
        except Exception as e:
            return JsonResponse({'error': f'LLM Error: {str(e)}'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required(login_url='/authentication/login/')
def index(request):
    """
    Render the home page
    """
    return render(request, 'home/index.html')

def govt_chatbot_view(request):
    return render(request, 'chatbot/govt_index.html')

def govt_process_chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('user_input', '')
            
            # Check if the input is empty
            if not user_input.strip():
                return JsonResponse({'error': 'Please enter a message'}, status=400)
            
            # Create the prompt with user input
            prompt = govt_prompt_template.format_messages(user_input=user_input)
            # Call the LLM directly
            response = llm.invoke(prompt)
            # Return the response
            return JsonResponse({'response': response.content})
        
        except Exception as e:
            return JsonResponse({'error': f'LLM Error: {str(e)}'}, status=500)

@login_required
def news_dashboard(request):
    """
    Render the news dashboard for the logged-in user
    Automatically fetches news based on user's profile
    """
    user_profile = request.user

    try:
        # Make API request to News Summarizer service
        api_url = 'http://192.168.1.113:8000/news'
        payload = {
            'topic': user_profile.location,  # Default to general news
            'location': 'in',
            'profession': user_profile.profession
        }

        response = requests.post(api_url, json=payload)
        response.raise_for_status()

        # Get news data
        news_data = response.json()

        context = {
            'news_summary': news_data.get('news_summary', 'No summary available'),
            'articles': news_data.get('articles', []),
            'user_country': 'in',
            'user_profession': user_profile.profession
        }

        return render(request, 'news/dashboard.html', context)

    except requests.RequestException as e:
        logger.error(f"News API request failed: {e}")
        return render(request, 'news/dashboard.html', {
            'error': 'Failed to fetch news. Please try again later.'
        })
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return render(request, 'news/dashboard.html', {
            'error': 'An unexpected error occurred.'
        })