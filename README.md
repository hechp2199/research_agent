# AI Biomedical Research Agent

An AI-powered biomedical literature research agent built with **Python and FastAPI**. It takes a research question, plans literature searches, retrieves papers from biomedical databases, ranks and deduplicates the results, evaluates evidence coverage, performs targeted refinement searches when necessary, and generates an evidence-grounded research summary using an LLM.

The project is designed to demonstrate practical **AI engineering, asynchronous programming, API integration, information retrieval, LLM integration, and agentic workflow orchestration**.

> **Note:** This project is a biomedical literature research assistant. It is not intended to provide medical advice, diagnosis, or clinical recommendations.

---

## Features

- **Research planning** using an LLM to break a broad research question into targeted search queries.
- **Multi-source literature retrieval** from:
  - PubMed
  - Europe PMC
- **Asynchronous source searching** using `asyncio` and `httpx`.
- **Structured paper representation** using Pydantic models.
- **Duplicate removal** using DOI, PMID, PMCID, and normalized title matching.
- **Hybrid relevance ranking** combining:
  - TF-IDF lexical similarity
  - PubMedBERT semantic similarity
- **Evidence assessment** to determine whether the retrieved literature sufficiently addresses the research question.
- **Targeted search refinement** based on identified evidence gaps.
- **Bounded iterative research** to avoid uncontrolled search and LLM calls.
- **LLM-based evidence synthesis** using either Google Gemini or OpenAI.
- **Configurable LLM provider** through environment variables.
- **LangGraph implementation** of the research workflow.
- **Logging and research state tracking** for easier debugging and workflow tracing.

---

## Research Workflow

The agent follows an iterative research workflow rather than simply searching for papers and summarizing them.

```text
                    Research Question
                           │
                           ▼
                  ┌─────────────────┐
                  │ Research Planner│
                  └────────┬────────┘
                           │
                    Search Queries
                           │
                           ▼
              ┌─────────────────────────┐
              │ PubMed + Europe PMC     │
              │ Concurrent Retrieval    │
              └────────────┬────────────┘
                           │
                           ▼
                     Deduplication
                           │
                           ▼
                   Relevance Ranking
                           │
                  ┌────────┴────────┐
                  │                 │
                TF-IDF         PubMedBERT
                  │                 │
                  └────────┬────────┘
                           │
                           ▼
                    Evidence Set
                           │
                           ▼
                  Evidence Assessment
                           │
                 ┌─────────┴─────────┐
                 │                   │
             Sufficient          Insufficient
                 │                   │
                 │                   ▼
                 │          Generate Refinement
                 │              Queries
                 │                   │
                 │                   ▼
                 │            Search Again
                 │                   │
                 │                   └───────┐
                 │                           │
                 └───────────────────────────┘
                             │
                             ▼
                    Final Evidence Set
                             │
                             ▼
                     LLM Synthesis
                             │
                             ▼
                    Research Summary
```

The refinement loop is bounded to a maximum of **two search iterations**.

---

## Relevance Ranking

The project uses a hybrid ranking approach combining lexical and semantic similarity.

### TF-IDF

TF-IDF is calculated independently for the paper title and abstract:

```text
TF-IDF Score =
    0.7 × Title Similarity
  + 0.3 × Abstract Similarity
```

This provides stronger importance to terminology appearing in the paper title.

### PubMedBERT

The semantic ranker uses:

```text
NeuML/pubmedbert-base-embeddings
```

The query, titles, and abstracts are encoded separately:

```text
Embedding Score =
    0.7 × Title Similarity
  + 0.3 × Abstract Similarity
```

Titles and abstracts are batch encoded to avoid performing individual model inference for every paper.

### Hybrid Ranking

The TF-IDF and embedding scores are min-max normalized within the current candidate set and combined:

```text
Hybrid Score =
    0.7 × Normalized PubMedBERT Score
  + 0.3 × Normalized TF-IDF Score
```

This allows the system to combine:

- **TF-IDF** → exact terminology and lexical relevance
- **PubMedBERT** → semantic and contextual relevance

The ranking weights are currently practical baseline values and can be tuned later using a labeled relevance dataset.

---

## Agentic Research Workflow

The project implements two versions of the research workflow.

### Standard Pipeline

The `/research/search` endpoint runs the research workflow directly through the service layer:

```text
Plan
 ↓
Search
 ↓
Deduplicate
 ↓
Rank
 ↓
Assess Evidence
 ↓
Refine if necessary
 ↓
Search Again
 ↓
Final Ranking
 ↓
Synthesize
```

### LangGraph Workflow

The `/research/graph_search` endpoint implements the workflow using **LangGraph**.

The graph contains nodes for:

- `plan`
- `search`
- `prepare_evidence`
- `assess_evidence`
- `refine`
- `synthesize`

The evidence assessment determines the next step:

```text
                 ┌──────────────┐
                 │   Evidence   │
                 │  Assessment  │
                 └──────┬───────┘
                        │
              ┌─────────┴─────────┐
              │                   │
          Sufficient          Insufficient
              │                   │
              ▼                   ▼
         Synthesize            Refine
                                  │
                                  ▼
                                Search
                                  │
                                  └──→ Assess
```

This provides an explicit stateful representation of the research workflow.

---

## Architecture

```text
app/
│
├── api/
│   └── routes/
│       ├── pubmed.py
│       ├── europe_pmc.py
│       └── research.py
│
├── schemas/
│   ├── paper.py
│   └── research.py
│
├── services/
│   ├── planner.py
│   ├── search.py
│   ├── research.py
│   ├── research_graph.py
│   ├── evidence.py
│   ├── refinement.py
│   ├── summarizer.py
│   │
│   ├── literature/
│   │   ├── pubmed.py
│   │   └── europe_pmc.py
│   │
│   └── llm/
│       ├── client.py
│       └── prompts.py
│
└── utils/
    ├── deduplication.py
    ├── json_parser.py
    ├── logger.py
    ├── min_max_norm.py
    ├── paper_formatter.py
    ├── search_query.py
    │
    └── ranking/
        ├── relevance.py
        ├── embedding_relevance.py
        └── hybrid_relevance.py
```

### Layer responsibilities

| Layer | Responsibility |
|---|---|
| `api/routes` | FastAPI HTTP endpoints |
| `schemas` | Pydantic request, response, paper, and research-state models |
| `services/literature` | PubMed and Europe PMC API integration |
| `services/planner` | Research-query planning |
| `services/search` | Concurrent literature-source orchestration |
| `services/research` | Main research workflow |
| `services/research_graph` | LangGraph-based workflow |
| `services/evidence` | Evidence sufficiency assessment |
| `services/refinement` | Targeted search refinement |
| `services/summarizer` | Final research synthesis |
| `services/llm` | LLM provider and prompt handling |
| `utils/ranking` | TF-IDF, embedding, and hybrid ranking |
| `utils/deduplication` | Cross-source duplicate removal |

---

## API Endpoints

### Health / Root

```http
GET /
```

### PubMed Search

```http
GET /pubmed/search
```

Parameters:

```text
query   - research query
limit   - maximum number of papers (1–100)
```

Example:

```text
/pubmed/search?query=deep+learning+knee+abnormality&limit=10
```

### Europe PMC Search

```http
GET /europe-pmc/search
```

Parameters:

```text
query   - research query
limit   - maximum number of papers (1–100)
```

### Research Agent

```http
POST /research/search
```

Request:

```json
{
  "query": "lightweight deep learning for meniscus tear detection",
  "limit": 10,
  "top_k": 5
}
```

### LangGraph Research Agent

```http
POST /research/graph_search
```

Uses the LangGraph implementation of the research workflow.

---

## Example Research Flow

For a query such as:

```text
lightweight deep learning for meniscus tear detection
```

the system can:

1. Generate targeted literature-search queries.
2. Select PubMed and Europe PMC as sources.
3. Search both sources concurrently.
4. Convert results into a common `Paper` representation.
5. Remove duplicate papers.
6. Rank papers using TF-IDF and PubMedBERT.
7. Evaluate the top-ranked evidence.
8. Identify missing evidence aspects.
9. Generate targeted refinement queries.
10. Search for additional evidence.
11. Re-rank the combined literature.
12. Select the final evidence set.
13. Generate an evidence-grounded summary.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- asyncio
- httpx

### Biomedical Literature

- PubMed / NCBI E-utilities
- Europe PMC REST API

### Information Retrieval / ML

- scikit-learn
- Sentence Transformers
- PubMedBERT embeddings
- cosine similarity
- TF-IDF
- min-max normalization

### LLM / Agentic AI

- Google Gemini API
- OpenAI API
- LangGraph

### Configuration

- python-dotenv
- Environment variables for API keys and model selection

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd research_agent-main
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

For Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model
```

Or for OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=your_openai_model
```

Only the API key for the selected provider is required.

### 5. Run the application

From the project root:

```bash
fastapi dev app/main.py
```

The FastAPI server will start locally.

Interactive API documentation is available through FastAPI's automatically generated Swagger/OpenAPI interface.

---

## Project Design Principles

The project follows a few deliberate design principles:

- Keep literature-source integrations separate from research orchestration.
- Use asynchronous execution for independent network-bound operations.
- Normalize external literature data into a common Pydantic model.
- Perform deterministic processing such as deduplication and ranking before final LLM synthesis.
- Use evidence assessment to determine whether additional searching is necessary.
- Prefer targeted refinement over uncontrolled repeated searches.
- Keep LLM provider configuration separate from the research workflow.
- Maintain a bounded research loop to control API and LLM usage.
- Keep the implementation modular and understandable.

---

### Future Improvements

Potential areas for further development include:

- Persistent research-state / trace storage
- More detailed citation and evidence traceability
- Additional biomedical literature sources
- Automated evaluation of ranking quality
- Persistent embedding caching
- More comprehensive automated tests
- Improved API error/status handling
- Further refinement of search-query generation

---

## Disclaimer

This project is intended for **research and educational purposes**. It retrieves and summarizes scientific literature and should not be used as a substitute for professional medical advice, diagnosis, or treatment.
