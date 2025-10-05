from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import supabase
from routers import configurations, webhooks, calls

load_dotenv()

app = FastAPI(title="Logistics Voice Agent API")

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

@app.get("/")
def read_root():
    return {"message": "Logistics Voice Agent API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/test-db")
def test_database():
    try:
        result = supabase.table("agent_configurations").select("*").execute()
        return {
            "status": "success",
            "message": "Database connection successful",
            "tables_accessible": True,
            "configurations_count": len(result.data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
