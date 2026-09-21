export interface Paper {
    pmid: string | null
    title: string
    abstract: string | null
    authors: string[]
    journal: string | null
    publication_date: string | null
    doi: string | null
    pmcid: string | null
    source: string
}

export interface ResearchRequest {
    query: string
    limit: number
    top_k: number
}

export interface ResearchResult {
    papers: Paper[]
    sources: Record<string, string>
    summary: string
}

const API_URL = 'http://localhost:8000'

export async function performResearch(
    request: ResearchRequest,
): Promise<ResearchResult> {
    const response = await fetch(
        `${API_URL}/research/graph_search`,
        {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(request),
        },
    )

    if (!response.ok) {
        throw new Error('Research request failed')
    }

    return response.json()
}