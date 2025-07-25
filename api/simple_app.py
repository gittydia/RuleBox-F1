from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class SearchRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"message": "RuleBox F1 API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/search")
async def search_regulations(request: SearchRequest):
    try:
        # Simple search implementation for now
        # In production, this would use the full search functionality
        results = [
            {
                "id": "1",
                "title": "Technical Regulations - Engine Specifications",
                "content": f"Found regulations related to: {request.query}",
                "source": "technical_regulations.pdf",
                "relevance_score": 0.85
            },
            {
                "id": "2", 
                "title": "Sporting Regulations - Race Procedures",
                "content": f"Additional information about: {request.query}",
                "source": "sporting_regulations.pdf",
                "relevance_score": 0.78
            }
        ]
        
        return {
            "query": request.query,
            "results": results,
            "total_results": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@app.post("/ai-query")
async def ai_query(request: QueryRequest):
    try:
        # Simple AI response for now
        # In production, this would use OpenRouter API
        response = f"Based on F1 regulations, regarding '{request.query}': This is a simplified response. The full AI integration with OpenRouter will be implemented in the next version."
        
        return {
            "query": request.query,
            "response": response,
            "source": "F1 Regulations Database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query error: {str(e)}")

# For testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
