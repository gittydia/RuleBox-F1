import json

def handler(request):
    """Simple Vercel handler for testing"""
    if request.method == "GET":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"message": "API is working!"})
        }
    
    if request.method == "POST":
        try:
            # Parse the request body
            if hasattr(request, 'body'):
                body = json.loads(request.body if isinstance(request.body, str) else request.body.decode('utf-8'))
            else:
                body = {}
            
            query = body.get("query", "test")
            
            # Return search results
            if "/search" in request.url:
                results = [
                    {
                        "_id": "1",
                        "title": "Technical Regulations - Engine Specifications",
                        "content": f"Found regulations related to: {query}",
                        "source": "technical_regulations.pdf",
                        "relevance_score": 0.85
                    }
                ]
                response_data = {"results": results}
            else:
                # AI query response
                response_data = {
                    "query": query,
                    "response": f"AI Response for '{query}': The backend is working! This confirms the API is successfully deployed.",
                    "source": "F1 Regulations Database"
                }
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps(response_data)
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
    
    # Handle OPTIONS for CORS
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS"
            },
            "body": ""
        }
    
    return {
        "statusCode": 405,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"error": "Method not allowed"})
    }
