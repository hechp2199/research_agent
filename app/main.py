import os
from fastapi import FastAPI
from google import genai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
gemini_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key)

@app.get("/")
async def root():
    return {"message": "Hello, This is Medical Research Agent API"}


@app.get("/test_gemini")
async def test_gemini():
    interaction = client.interactions.create(
            model="gemini-3.6-flash",
            input="What model is this? Answer in one word"
    )
    return {"message": interaction.output_text}