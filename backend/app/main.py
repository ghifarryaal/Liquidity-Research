"""
LiquidityResearch — FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.routers import cluster, chat

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------

app = FastAPI(
    title="LiquidityResearch API",
    description=(
        "No-login stock analysis platform for Indonesian equity indices "
        "(LQ45 & KOMPAS 100) using ML clustering and technical indicators."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow Next.js dev & prod origins
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(cluster.router, prefix="/api", tags=["Clustering"])
app.include_router(chat.router, prefix="/api", tags=["AI Mentor"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/", tags=["Health"])
async def root():
    return JSONResponse(
        content={
            "status": "ok",
            "service": "LiquidityResearch API",
            "version": "1.0.0",
            "endpoints": {
                "cluster": "/api/cluster/{index_name}",
                "stock_detail": "/api/stock/{ticker}",
                "docs": "/docs",
            },
        }
    )


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
