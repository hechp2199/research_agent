import os

from dotenv import load_dotenv
from google import genai
from openai import OpenAI

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()


if LLM_PROVIDER == "gemini":
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)
    MODEL = "gemini-3.6-flash"


elif LLM_PROVIDER == "openai":
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = OpenAI(api_key=api_key)
    MODEL = "gpt-5.6-luna"


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
