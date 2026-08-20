def build_research_plan_prompt(query: str) -> str:
    return f"""
You are a biomedical literature research assistant.

Research question:
{query}

Develop a literature search plan for this research question.

The plan should:
1. Generate 2 to 4 precise biomedical literature search queries.
2. Identify the most relevant literature databases from:
   - pubmed
   - europe_pmc
3. Make the queries complementary rather than redundant.
4. Cover important aspects of the research question.
5. Use terminology appropriate for biomedical literature databases.
6. Do not invent concepts unrelated to the research question.

Return ONLY valid JSON in exactly this structure:

{{
    "search_queries": [
        "query 1",
        "query 2"
    ],
    "sources": [
        "pubmed",
        "europe_pmc"
    ],
    "reasoning": "Brief explanation of the search strategy."
}}
"""


def build_evidence_assessment_prompt(
    query: str,
    papers_text: str,
) -> str:
    return f"""
You are a biomedical literature research assistant.

Research question:
{query}

The following papers were retrieved:

{papers_text}

Assess whether the retrieved literature provides sufficient
evidence to address the research question.

Distinguish between:

1. Missing aspects:
   Important aspects of the research question that are not
   adequately covered by the retrieved literature.

2. Evidence gaps:
   Limitations or weaknesses in the available evidence, such as
   limited validation, small datasets, heterogeneous methods,
   or limited clinical applicability.

Do not treat an evidence gap as a missing aspect unless it
prevents the research question from being adequately addressed.

Return ONLY valid JSON in exactly this structure:

{{
    "sufficient": true,
    "reasoning": "Brief explanation of whether the research question is adequately covered.",
    "missing_aspects": [
        "aspect that is not adequately covered"
    ],
    "evidence_gaps": [
        "limitation or weakness in the available evidence"
    ]
}}

Rules:
- Set sufficient to true if the literature adequately covers the
  main aspects of the research question, even if evidence gaps remain.
- Set sufficient to false when important aspects of the research
  question remain unanswered.
- Base the assessment only on the provided papers.
- Do not invent information.
- Do not provide medical advice or clinical recommendations.
"""


def build_search_refinement_prompt(
    query: str,
    missing_aspects: list[str],
) -> str:

    missing_text = "\n".join(f"- {aspect}" for aspect in missing_aspects)

    return f"""
You are a biomedical literature research assistant.

Original research question:
{query}

The initial literature search was not sufficient.

The following aspects of the research question are still
insufficiently covered:

{missing_text}

Generate targeted biomedical literature search queries that
specifically address these missing aspects.

Rules:
1. Generate 1 to 3 targeted search queries.
2. Focus only on the missing aspects.
3. Do not simply repeat the original search queries.
4. Use terminology appropriate for biomedical literature databases.
5. Keep the queries reasonably precise.
6. Do not invent concepts unrelated to the missing aspects.
7. Focus on retrieving relevant scientific literature rather
   than providing medical advice or clinical recommendations.

Return ONLY valid JSON in exactly this structure:

{{
    "search_queries": [
        "query 1",
        "query 2"
    ],
    "reasoning": "Brief explanation of how these queries address the missing aspects."
}}
"""


def build_research_summary_prompt(
    query: str,
    papers_text: str,
) -> str:
    return f"""
You are a biomedical literature research assistant.

Research question:
{query}

Below are papers retrieved from biomedical literature databases.

{papers_text}

Based only on the information provided above:

1. Summarize the key findings relevant to the research question.
2. Identify common themes across the papers.
3. Mention important differences or conflicting findings.
4. Mention relevant limitations if available.
5. Do not invent information that is not present in the papers.
6. Do not provide medical advice or clinical recommendations.

Provide a concise, evidence-grounded research summary.
"""
