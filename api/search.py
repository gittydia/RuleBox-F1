from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    query: str

def handler(request):
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body)
            query = body.get("query", "")
            
            # Simple search implementation
            results = [
                {
                    "id": "1",
                    "title": "Technical Regulations - Engine Specifications",
                    "content": f"Found regulations related to: {query}",
                    "source": "technical_regulations.pdf",
                    "relevance_score": 0.85
                },
                {
                    "id": "2", 
                    "title": "Sporting Regulations - Race Procedures",
                    "content": f"Additional information about: {query}",
                    "source": "sporting_regulations.pdf",
                    "relevance_score": 0.78
                }
            ]
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({
                    "query": query,
                    "results": results,
                    "total_results": len(results)
                })
            }
        except Exception as e:
            return {
                "statusCode": 500,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"error": str(e)})
            }
    
    elif request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": ""
        }
    
    return {
        "statusCode": 405,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Method not allowed"})
    }
