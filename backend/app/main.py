"""
LiquidityResearch — FastAPI Backend Entry Point
"""

import os
import traceback

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app.routers import cluster, chat, ai_assistant

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

ALLOWED_ORIGINS_RAW = os.getenv("ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [o.strip() for o in ALLOWED_ORIGINS_RAW.split(",")]

# If wildcard is used, credentials must be False (browser restriction)
_use_wildcard = ALLOWED_ORIGINS == ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=not _use_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(cluster.router, prefix="/api", tags=["Clustering"])
app.include_router(chat.router, prefix="/api", tags=["AI Mentor"])
app.include_router(ai_assistant.router, tags=["AI Assistant"])

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}", "traceback": tb}
    )


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
