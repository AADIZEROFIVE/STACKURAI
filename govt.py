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

prompt_template = ChatPromptTemplate.from_messages([
    ("system", """You are an assistant providing information on government subsidies and benefits.
      respond with a numbered list of available schemes and their short descriptions.
      let the values and steps be on top and explanation later.
      Do not add extra explanations, greetings, or unrelated information.
      include msp's and other related information. Be on point and give values when asked about prices.
     """),
    ("human", "{user_input}")
])

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