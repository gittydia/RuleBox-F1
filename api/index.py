def handler(event, context):
    """Vercel Python handler"""
    import json
    
    # Get the HTTP method and path
    method = event.get('httpMethod', 'GET')
    path = event.get('path', '')
    
    # CORS headers
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
    }
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': ''
        }
    
    # Handle GET requests
    if method == 'GET':
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'message': 'API is working!', 'path': path})
        }
    
    # Handle POST requests
    if method == 'POST':
        try:
            # Parse request body
            body = event.get('body', '{}')
            if isinstance(body, str):
                data = json.loads(body)
            else:
                data = body
            
            query = data.get('query', 'test')
            
            # Return different responses based on path
            if 'search' in path:
                response_data = {
                    'results': [
                        {
                            '_id': '1',
                            'title': 'Technical Regulations - Engine Specifications',
                            'content': f'Found regulations related to: {query}',
                            'source': 'technical_regulations.pdf',
                            'relevance_score': 0.85
                        }
                    ]
                }
            else:
                response_data = {
                    'query': query,
                    'response': f'AI Response for "{query}": The backend is working! API is successfully deployed.',
                    'source': 'F1 Regulations Database'
                }
            
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(response_data)
            }
            
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': str(e), 'type': 'Internal Server Error'})
            }
    
    # Method not allowed
    return {
        'statusCode': 405,
        'headers': headers,
        'body': json.dumps({'error': 'Method not allowed'})
    }
