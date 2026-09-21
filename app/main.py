from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.pubmed import router as pubmed_router
from app.api.routes.europe_pmc import router as europe_pmc_router
from app.api.routes.research import router as research_router

app = FastAPI(
    title="AI Biomedical Research Agent",
    description="API for scientific literature research and retrieval",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pubmed_router)
app.include_router(europe_pmc_router)
app.include_router(research_router)


@app.get("/")
async def root():
    return {"message": "Hello, This is Medical Research Agent API"}
