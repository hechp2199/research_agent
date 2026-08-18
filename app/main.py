import os
from fastapi import FastAPI
from google import genai
from dotenv import load_dotenv

from app.api.routes.pubmed import router as pubmed_router
from app.api.routes.europe_pmc import router as europe_pmc_router
from app.api.routes.research import router as research_router

load_dotenv()

app = FastAPI(
    title="AI Medical Research Agent",
    description="API for scientific literature research and retrieval",
)
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    raise RuntimeError("GEMINI_API_KEY is not set")
client = genai.Client(api_key=gemini_key)

app.include_router(pubmed_router)
app.include_router(europe_pmc_router)
app.include_router(research_router)


@app.get("/")
async def root():
    return {"message": "Hello, This is Medical Research Agent API"}


@app.get("/test_gemini")
async def test_gemini():
    interaction = client.interactions.create(
        model="gemini-3.6-flash", input="What model is this? Answer in one word"
    )
    return {"message": interaction.output_text}
