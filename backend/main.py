from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from database import supabase

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Logistics Voice Agent API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Logistics Voice Agent API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/test-db")
def test_database():
    """Test database connection"""
    try:
        # Try to query the agent_configurations table
        result = supabase.table("agent_configurations").select("*").execute()
        return {
            "status": "success",
            "message": "Database connection successful",
            "tables_accessible": True,
            "configurations_count": len(result.data)
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
