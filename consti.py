from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")
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
# Example User Queries Your Chatbot Can Handle
# "How do I file an FIR if the police refuse?"
# "What are my rights if I get arrested?"
# "How do I get a caste certificate?"
# "What is the process for divorce?"
# "Can my employer fire me without notice?"
# "What are my rights if someone grabs my land illegally?"
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
      Be on point and give whats the neccesity only if the user asks for it
     """),
    ("human", "{user_input}")
])
# on point line is necessary so that if user is in delima then he wont be harrased to understand concepts but get ways to execute.

# Define request body model
class ChatRequest(BaseModel):
    user_input: str

# Initialize FastAPI app
app = FastAPI(title="Gemini Chatbot API")

# Define the chatbot endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get the user input
        user_input = request.user_input

        # Create the prompt with user input
        prompt = prompt_template.format_messages(user_input=user_input)

        # Call the LLM
        response = llm.invoke(prompt)

        # Return the response
        return {"response": response.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="172.26.128.1", port=8080)
