from django.shortcuts import render
import json
from django.http import JsonResponse
from django.conf import settings
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from django.contrib.auth.decorators import login_required

# Load environment variables
load_dotenv("../.env")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Check if API key is available
if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    api_key=GEMINI_API_KEY,
    temperature=0,
    timeout=60,
    max_retries=2
)

# Define a prompt template for the chatbot
prompt_template = ChatPromptTemplate.from_messages([
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
            prompt = prompt_template.format_messages(user_input=user_input)
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