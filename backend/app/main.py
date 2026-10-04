"""
MAIN FASTAPI ENTRYPOINT
=======================
Initializes the FastAPI application, configures CORS middleware,
and registers all API routes:
- /api/chat (5-agent pipeline)
- /api/tips (Nutrition tips and food safety news)
- /api/auth (User registration and authentication)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.chat import router as chat_router
from backend.app.api.tips import router as tips_router
from backend.app.api.auth import router as auth_router

app = FastAPI(
    title="NutriGuard - SmartRecipe AI API",
    description="Agentic Multi-Agent Recipe Recommendation & Food Safety System (IT 3041)",
    version="1.0.0"
)

# Configure CORS Middleware to allow requests from Streamlit UI or local clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(chat_router, prefix="/api")
app.include_router(tips_router, prefix="/api")
app.include_router(auth_router, prefix="/api")


@app.get("/", tags=["Health Check"])
def health_check():
    """System health check endpoint."""
    return {
        "status": "online",
        "service": "NutriGuard SmartRecipe AI",
        "version": "1.0.0",
        "agents": ["QueryAgent", "RetrievalAgent", "SafetyAgent", "RankingAgent", "ResponseAgent"]
    }
