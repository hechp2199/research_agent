from app.schemas.research import SearchRefinement
from app.services.llm.client import generate
from app.services.llm.prompts import build_search_refinement_prompt
from app.utils.json_parser import parse_json_response


async def generate_refinement_queries(
    query: str,
    missing_aspects: list[str],
) -> SearchRefinement:

    prompt = build_search_refinement_prompt(
        query,
        missing_aspects,
    )

    try:
        output = generate(prompt)

        refinement_data = parse_json_response(output)

        return SearchRefinement.model_validate(refinement_data)

    except Exception as e:
        raise RuntimeError("Search refinement failed") from e
