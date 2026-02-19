"""
Point d'entrée principal de l'API FastAPI
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1 import offers, stats, analytics, filters as filters_router

# Création de l'application FastAPI
app = FastAPI(
    title="JobMarket API",
    description="API pour le dashboard d'analyse du marché de l'emploi data en France",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routes
app.include_router(offers.router, prefix="/api/v1/offers", tags=["Offers"])
app.include_router(stats.router, prefix="/api/v1/stats", tags=["Statistics"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
app.include_router(filters_router.router, prefix="/api/v1/filters", tags=["Filters"])


@app.get("/")
async def root():
    """Root endpoint - health check"""
    return {
        "name": "JobMarket API",
        "version": "0.1.0",
        "status": "healthy",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
