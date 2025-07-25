from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "RuleBox F1 API is running!"}

@app.get("/api/")
async def api_root():
    return {"message": "API endpoint is working!"}

@app.post("/api/search")
async def search(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        
        results = [
            {
                "_id": "1",
                "title": "Technical Regulations - Engine Specifications",
                "content": f"Found regulations related to: {query}",
                "source": "technical_regulations.pdf",
                "relevance_score": 0.85
            }
        ]
        
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/ai-query") 
async def ai_query_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query", "")
        
        response = f"AI Response for '{query}': The backend is working! This confirms the API is successfully deployed and responding."
        
        return {
            "query": query,
            "response": response,
            "source": "F1 Regulations Database"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")
