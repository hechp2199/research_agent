import re

from app.schemas.paper import Paper

TITLE_REGEX = re.compile(r"[^a-z0-9]")
DOI_PREFIX_REGEX = re.compile(
    r"^(?:https?://)?(?:dx\.)?doi\.org/|^\s*doi:\s*",
    re.IGNORECASE,
)
PMC_PREFIX_REGEX = re.compile(r"^PMC", re.IGNORECASE)


def normalize_title(title: str) -> str:
    """Normalize a paper title for comparison."""
    return TITLE_REGEX.sub("", title.lower())


def normalize_doi(doi: str) -> str:
    """Normalize DOI by removing common URL prefixes."""
    doi = doi.strip().lower()
    return DOI_PREFIX_REGEX.sub("", doi)


def normalize_pmcid(pmcid: str) -> str:
    """Normalize PMCID by removing the PMC prefix."""
    pmcid = pmcid.strip().upper()
    return PMC_PREFIX_REGEX.sub("", pmcid)


def deduplicate_papers(papers: list[Paper]) -> list[Paper]:
    """Remove duplicate papers using DOI, PMID, and PMCID first.

    Title is used only as a fallback when none of the stronger
    identifiers are present.
    """

    seen_dois = set()
    seen_pmids = set()
    seen_pmcids = set()
    seen_titles = set()

    unique_papers = []

    for paper in papers:
        is_duplicate = False
        has_strong_identifier = False

        # Check DOI
        if paper.doi:
            doi = normalize_doi(paper.doi)
            if doi:
                has_strong_identifier = True

                if doi in seen_dois:
                    is_duplicate = True

                seen_dois.add(doi)

        # Check PMID
        if paper.pmid:
            pmid = paper.pmid.strip()
            if pmid:
                has_strong_identifier = True

                if pmid in seen_pmids:
                    is_duplicate = True

                seen_pmids.add(pmid)

        # Check PMCID
        if paper.pmcid:
            pmcid = normalize_pmcid(paper.pmcid)
            if pmcid:
                has_strong_identifier = True

                if pmcid in seen_pmcids:
                    is_duplicate = True

                seen_pmcids.add(pmcid)

        # Fallback to title only if no strong identifier exists
        if not has_strong_identifier and paper.title:
            title = normalize_title(paper.title)

            if title:
                if title in seen_titles:
                    is_duplicate = True

                seen_titles.add(title)

        if is_duplicate:
            continue

        unique_papers.append(paper)

    return unique_papers
