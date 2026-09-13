import os

from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL","gemini-3.6-flash").lower() 
OPENAI_MODEL = os.getenv("OPENAI_MODEL","gpt-5.6-luna").lower()

if LLM_PROVIDER == "gemini":
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)
    MODEL = GEMINI_MODEL


elif LLM_PROVIDER == "openai":
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    MODEL = OPENAI_MODEL


else:
    raise RuntimeError(f"Unsupported LLM provider: {LLM_PROVIDER}")


def generate(prompt: str) -> str:

    if LLM_PROVIDER == "gemini":
        response = client.interactions.create(
            model=MODEL,
            input=prompt,
        )

        return response.output_text

    response = client.responses.create(
        model=MODEL,
        input=prompt,
    )

    return response.output_text
