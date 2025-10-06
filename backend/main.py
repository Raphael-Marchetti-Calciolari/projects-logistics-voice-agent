"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from routers import configurations, webhooks, calls
from startup import initialize_agents
from logger import app_logger
import asyncio

load_dotenv()

app = FastAPI(
    title="Logistics Voice Agent API",
    description="API for managing AI-powered logistics voice calls",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(configurations.router)
app.include_router(webhooks.router)
app.include_router(calls.router)


@app.on_event("startup")
async def startup_event():
    """Run initialization on startup."""
    app_logger.info("Starting Logistics Voice Agent API")
    
    # Run agent initialization in background
    asyncio.create_task(initialize_agents())


# PUBLIC_INTERFACE
@app.get("/", tags=["health"])
def read_root():
    """
    Root endpoint.
    
    Returns:
        Welcome message
    """
    return {"message": "Logistics Voice Agent API is running"}


# PUBLIC_INTERFACE
@app.get("/health", tags=["health"])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {"status": "healthy"}
