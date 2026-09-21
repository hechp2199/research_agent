import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { performResearch } from './api/researchApi'
import type { ResearchResult } from './api/researchApi'
import PaperCard from './components/PaperCard'
import ResearchLoader from './components/ResearchLoader'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [limit, setLimit] = useState(10)
  const [topK, setTopK] = useState(5)
  const [result, setResult] = useState<ResearchResult | null>(null)
  const [loading, setLoading] = useState(false)

  const handleResearch = async () => {
    setLoading(true)
    try {
      const researchResult = await performResearch({
        query,
        limit,
        top_k: topK,
      })

      setResult(researchResult)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="app">
      <section className="search-container">
        <h1>AI Biomedical Research Agent</h1>

        <p className="subtitle">
          Search biomedical literature and generate an evidence-grounded summary.
        </p>

        <label htmlFor="query">
          Research question
        </label>

        <textarea
          id="query"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="What would you like to research?"
          rows={5}
        />

        <div className="options">
          <div className="option">
            <label htmlFor="limit">
              Papers per source
            </label>

            <input
              id="limit"
              type="number"
              min="1"
              max="100"
              value={limit}
              onChange={(event) => setLimit(Number(event.target.value))}
            />
          </div>

          <div className="option">
            <label htmlFor="topK">
              Final papers
            </label>

            <input
              id="topK"
              type="number"
              min="1"
              max="20"
              value={topK}
              onChange={(event) => setTopK(Number(event.target.value))}
            />
          </div>
        </div>

        <button
          onClick={handleResearch}
          disabled={loading}
        >
          {loading ? 'Researching...' : 'Research'}
        </button>
      </section>
      {loading && <ResearchLoader />}
      {result && !loading && (
        <section className="results">
          <h2>Research Result</h2>

          <div className="sources">
            <h3>Sources</h3>

            <div className="source-list">
              {Object.entries(result.sources).map(([source, status]) => (
                <div key={source} className="source-item">
                  <span>{status === 'success' ? '✓' : '✗'}</span>
                  <span>{source}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="summary">
            <ReactMarkdown>
              {result.summary}
            </ReactMarkdown>
          </div>

          <div className="papers">
            <h2>Research Papers</h2>

            <div className="paper-list">
              {result.papers.map((paper) => (
                <PaperCard
                  key={paper.pmid ?? paper.title}
                  paper={paper}
                />
              ))}
            </div>
          </div>

          <p>
            Papers retrieved: {result.papers.length}
          </p>
        </section>
      )}
    </main>
  )
}

export default App