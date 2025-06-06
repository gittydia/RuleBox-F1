from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datacollect import RuleBoxF1Processor
from ai_functions import ai_query  # Import the AI query function
import os
import uvicorn
# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to restrict origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the RuleBoxF1Processor
processor = RuleBoxF1Processor(
    mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY")
)

@app.post("/api/search")
async def search(request: Request):
    data = await request.json()
    query = data.get("query")

    if not query:
        raise HTTPException(status_code=400, detail="Query is required.")

    # Perform semantic search
    results = processor.semantic_search(query, limit=10)

     # Convert ObjectId to string for JSON serialization
    serialized_results = [
        {**result, "_id": str(result["_id"])} for result in results
    ]

    return JSONResponse(content={"results": serialized_results})

@app.post("/api/ai-query")
async def ai_query_endpoint(request: Request):
    try:
        # Attempt to parse JSON from the request body
        data = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid or empty JSON payload") from e

    # Validate required fields in the payload
    if "query" not in data or not isinstance(data["query"], str) or not data["query"].strip():
        raise HTTPException(status_code=400, detail="The 'query' field is required and must be a non-empty string.")

    # Optional: Validate other fields if necessary
    context_rules = data.get("context_rules")
    if context_rules is not None and not isinstance(context_rules, list):
        raise HTTPException(status_code=400, detail="The 'context_rules' field must be a list if provided.")

    # Call the AI query function
    response = ai_query(processor.ai_client, data["query"], context_rules)

    return JSONResponse(content={"response": response})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)