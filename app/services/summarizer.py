from app.schemas.paper import Paper
from app.services.llm.client import generate
from app.services.llm.prompts import build_research_summary_prompt
from app.utils.paper_formatter import format_papers


async def generate_research_summary(
    query: str,
    papers: list[Paper],
) -> str:

    papers_text = format_papers(papers)

    prompt = build_research_summary_prompt(
        query,
        papers_text,
    )

    try:
        return generate(prompt)

    except Exception as e:
        raise RuntimeError("Research summary generation failed") from e
