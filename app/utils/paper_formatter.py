from app.schemas.paper import Paper


def format_papers(papers: list[Paper]) -> str:
    return "\n\n".join(f"""
Title: {paper.title}
Authors: {", ".join(paper.authors)}
Journal: {paper.journal}
Publication Date: {paper.publication_date}
Abstract: {paper.abstract}
DOI: {paper.doi}
PMID: {paper.pmid}
PMCID: {paper.pmcid}
""" for paper in papers)
