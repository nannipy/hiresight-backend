import os
import sys

# Add current directory to sys.path to allow importing sibling modules in Vercel
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(root_path="/api")

# Configure CORS
origins = [
    "http://localhost:8080",  # Vite default port
    "http://127.0.0.1:8080",
    "https://hiresight-ce868112e8e9.herokuapp.com",  # Frontend production
    "*"  # Allow all origins (remove in production for security)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalysisRequest(BaseModel):
    job_id: str | None = None

@app.post("/analyze")
async def analyze_cvs(request: AnalysisRequest, background_tasks: BackgroundTasks):
    try:
        # Import here to avoid crashing at startup if Supabase env vars are missing
        import process_cvs
        
        # Run analysis in the background
        background_tasks.add_task(process_cvs.process_cvs, request.job_id)
        
        return {"message": "Analysis started in background", "status": "processing"}
    except Exception as e:
        print(f"Error starting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
