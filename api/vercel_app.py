from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

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

@app.get("/")
async def root():
    return {"message": "RuleBox F1 API is running!"}

@app.post("/api/search")
async def search(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        # Simplified search response (replace with actual search later)
        results = [
            {
                "_id": "1",
                "title": "Technical Regulations - Engine Specifications",
                "content": f"Found regulations related to: {query}",
                "source": "technical_regulations.pdf",
                "relevance_score": 0.85,
                "page_number": 15
            },
            {
                "_id": "2", 
                "title": "Sporting Regulations - Race Procedures",
                "content": f"Additional information about: {query}",
                "source": "sporting_regulations.pdf",
                "relevance_score": 0.78,
                "page_number": 23
            }
        ]
        
        return JSONResponse(content={"results": results})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/api/ai-query")
async def ai_query_endpoint(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        conversation_id = data.get("conversation_id")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        # Simplified AI response (replace with actual AI integration later)
        response = f"Based on F1 regulations, regarding '{query}': This is a working backend response! The AI integration is functional. The full OpenRouter integration will provide more detailed responses."
        
        return JSONResponse(content={
            "response": response,
            "conversation_id": conversation_id or "default",
            "source": "F1 Regulations Database"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@app.post("/auth/register")
async def register(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required.")
        
        # Simplified registration (replace with actual auth later)
        return JSONResponse(content={
            "message": "User registered successfully",
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required.")
        
        # Simplified login (replace with actual auth later)
        return JSONResponse(content={
            "access_token": "dummy_token_for_now",
            "token_type": "bearer",
            "username": username
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
