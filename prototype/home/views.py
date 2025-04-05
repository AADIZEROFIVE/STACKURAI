from django.shortcuts import render, redirect
import json
from django.http import JsonResponse, HttpResponseServerError
from django.conf import settings
import os
import logging
import traceback
import requests
from dotenv import load_dotenv
from django.contrib import messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Optional
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .forms import FinancialGoalForm

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

@login_required
def financial_dashboard(request):
    """
    Display user's financial dashboard with option to request a financial roadmap
    """
    # Get or create user profile
    user_profile = request.user
    
    # Check if we have necessary profile information
    profile_complete = all([
        user_profile.location,
        user_profile.income,
        user_profile.profession
    ])
    
    context = {
        'user_profile': user_profile,
        'profile_complete': profile_complete,
        'form': FinancialGoalForm()
    }
    
    return render(request, 'finance/financial_dashboard.html', context)

@login_required
@require_http_methods(["POST"])
def generate_financial_roadmap(request):
    """
    Generate a personalized financial roadmap based on the user's goal
    and existing profile information
    """
    form = FinancialGoalForm(request.POST)
    
    if not form.is_valid():
        messages.error(request, "Please provide a valid financial goal.")
        return redirect('financial_dashboard')
    
    # Get user profile information
    user_profile = request.user
    
    # Check if we have all the required profile information
    if not all([user_profile.location, user_profile.income, user_profile.profession]):
        messages.error(request, "Please complete your profile before generating a roadmap.")
        return redirect('index')
    
    # Extract form data
    financial_goal = form.cleaned_data['goal']
    
    # Prepare prompt for Gemini
    prompt = f"""
    Create a professional, personalized financial roadmap for a user with the following details:
    
    - Location: {user_profile.location}
    - Current Monthly Income: Rs{user_profile.income}
    - Profession: {user_profile.profession}
    - Education: {user_profile.education_qualification}
    - Financial Goal: {financial_goal}
    
    The roadmap should include:
    1. A clear assessment of the user's current financial situation based on their location, income, and profession
    2. A step-by-step plan to achieve their stated financial goal
    3. Specific actionable steps with timeframes
    4. Potential challenges to anticipate and how to overcome them
    5. Relevant investment vehicles or financial products that might help them reach their goal
    6. Tax considerations based on their location
    7. Recommendations for financial literacy resources specific to their situation
    8. Return the answer in HTML format
    Format the response as a professional financial advisory document with clear sections and bullet points where appropriate.
    """
    
    try:
        # Generate roadmap using Gemini
        response = llm.invoke(prompt)
        roadmap_content = response.content
        
        # Save the generated roadmap to the user's profile or a separate model if needed
        user_profile.last_roadmap = roadmap_content
        user_profile.save()
        
        context = {
            'user_profile': user_profile,
            'roadmap': roadmap_content,
            'goal': financial_goal
        }
        
        return render(request, 'finance/financial_roadmap.html', context)
        
    except Exception as e:
        messages.error(request, f"Error generating roadmap: {str(e)}")
        return redirect('financial_dashboard')