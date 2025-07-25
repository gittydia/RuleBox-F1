import json

def handler(request):
    # Handle CORS preflight
    if request.method == "OPTIONS":
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": ""
        }
    
    if request.method == "POST":
        try:
            # Parse the request body
            body = json.loads(request.body.decode('utf-8') if hasattr(request.body, 'decode') else request.body)
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
    
    return {
        "statusCode": 405,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps({"error": "Method not allowed"})
    }
