import type { Paper } from '../api/researchApi'

interface PaperCardProps {
    paper: Paper
}

function PaperCard({ paper }: PaperCardProps) {
    return (
        <article className="paper-card">
            <h3>{paper.title}</h3>

            <div className="paper-meta">
                {paper.journal && <span>{paper.journal}</span>}

                {paper.publication_date && (
                    <span>{paper.publication_date}</span>
                )}

                <span>{paper.source}</span>
            </div>

            {paper.authors.length > 0 && (
                <p className="paper-authors">
                    {paper.authors.join(', ')}
                </p>
            )}

            {paper.abstract && (
                <p className="paper-abstract">
                    {paper.abstract}
                </p>
            )}

            <div className="paper-links">
                {paper.pmid && (
                    <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${paper.pmid}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        PMID: {paper.pmid}
                    </a>
                )}

                {paper.pmcid && (
                    <a
                        href={`https://pmc.ncbi.nlm.nih.gov/articles/${paper.pmcid}/`}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        PMCID: {paper.pmcid}
                    </a>
                )}

                {paper.doi && (
                    <a
                        href={`https://doi.org/${paper.doi}`}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        DOI: {paper.doi}
                    </a>
                )}
            </div>
        </article>
    )
}

export default PaperCard