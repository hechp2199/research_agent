from app.schemas.paper import Paper
from app.schemas.research import EvidenceAssessment
from app.services.llm.client import generate
from app.services.llm.prompts import build_evidence_assessment_prompt
from app.utils.json_parser import parse_json_response
from app.utils.paper_formatter import format_papers


async def assess_evidence(
    query: str,
    papers: list[Paper],
) -> EvidenceAssessment:

    papers_text = format_papers(papers)

    prompt = build_evidence_assessment_prompt(
        query,
        papers_text,
    )

    try:
        output = generate(prompt)

        assessment_data = parse_json_response(output)

        return EvidenceAssessment.model_validate(assessment_data)

    except Exception as e:
        raise RuntimeError("Evidence assessment failed") from e
