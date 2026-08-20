from app.schemas.research import ResearchPlan
from app.services.llm.client import generate
from app.services.llm.prompts import build_research_plan_prompt
from app.utils.json_parser import parse_json_response


async def generate_research_plan(
    query: str,
) -> ResearchPlan:

    prompt = build_research_plan_prompt(query)

    try:
        output = generate(prompt)

        plan_data = parse_json_response(output)

        return ResearchPlan.model_validate(plan_data)

    except Exception as e:
        raise RuntimeError("Research planning failed") from e
