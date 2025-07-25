import sys
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
import json

# Import your backend modules (they're in the same directory now)
try:
    from datacollect import RuleBoxF1Processor
    from ai_functions import ai_query
    from auth import AuthHandler
    from motor.motor_asyncio import AsyncIOMotorClient
except ImportError as e:
    print(f"Import error: {e}")

app = FastAPI()

# Initialize components
try:
    db_client = AsyncIOMotorClient(os.getenv("MONGODB_URI", ""))
    processor = RuleBoxF1Processor(
        mongodb_uri=os.getenv("MONGODB_URI", ""),
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "")
    )
    auth_handler = AuthHandler(db_client)
except Exception as e:
    print(f"Initialization error: {e}")

@app.post("/api/search")
async def search(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        results = processor.semantic_search(query, limit=10)
        if not results:
            results = []
        
        serialized_results = []
        for result in results:
            if "_id" in result:
                result["_id"] = str(result["_id"])
            serialized_results.append(result)
        
        return JSONResponse(content={"results": serialized_results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/ai-query")
async def ai_query_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        response = await ai_query(query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

# Export for Vercel
def handler(event, context):
    return app
