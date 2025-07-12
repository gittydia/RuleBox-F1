from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datacollect import RuleBoxF1Processor
from ai_functions import ai_query
import os
import uvicorn
from dotenv import load_dotenv
from auth import AuthHandler
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

load_dotenv()

app = FastAPI()

# Add custom exception handler for HTTPException
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MongoDB client
db_client = AsyncIOMotorClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))

# Initialize the RuleBoxF1Processor
processor = RuleBoxF1Processor(
    mongodb_uri=os.getenv("MONGODB_URI", "mongodb://localhost:27017/"),
    openrouter_api_key=os.getenv("OPENROUTER_API_KEY", "")
)

auth_handler = AuthHandler(db_client)

@app.post("/auth/register")
async def register(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        email = data.get("email")
        
        print(f"Registration attempt for username: {username}, email: {email}")
        
        if not username or not password or not email:
            raise HTTPException(status_code=400, detail="Username, password, and email are required")
        
        success, message = await auth_handler.register_user(username, password, email)
        if not success:
            print(f"Registration failed for {username}: {message}")
            raise HTTPException(status_code=400, detail=message)
        
        print(f"Registration successful for {username}")
        return {"message": message, "success": True}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
async def login(request: Request):
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        
        print(f"Login attempt for username: {username}")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password are required")
        
        success, token_or_error = await auth_handler.authenticate_user(username, password)
        if not success:
            print(f"Authentication failed for {username}: {token_or_error}")
            raise HTTPException(status_code=401, detail=token_or_error)
        
        print(f"Authentication successful for {username}")
        return {"token": token_or_error}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/api/search")
async def search(request: Request):
    try:
        data = await request.json()
        query = data.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        # Perform semantic search
        results = processor.semantic_search(query, limit=10)
        
        if not results:
            results = []
        
        # Convert ObjectId to string for JSON serialization
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
        conversation_id = data.get("conversation_id")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required.")
        
        # Use the ai_query function from ai_functions module
        try:
            response = await ai_query(query)
        except Exception as ai_error:
            print(f"AI function error: {str(ai_error)}")
            raise ai_error
        
        # Ensure the response is JSON serializable
        if hasattr(response, '__dict__'):
            response = response.__dict__
        elif not isinstance(response, (str, int, float, bool, list, dict, type(None))):
            response = str(response)
        
        return {"response": response}
    except Exception as e:
        print(f"AI query error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI query failed: {str(e)}")

@app.post("/api/ingest-data")
async def ingest_data():
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, processor.process_documents)
        return JSONResponse(content={"message": "Data ingestion completed", "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")

@app.get("/api/data-status")
async def data_status():
    try:
        db = processor.db
        collections_count = {}
        collection_names = db.list_collection_names()
        
        for collection_name in collection_names:
            count = db[collection_name].count_documents({})
            collections_count[collection_name] = count
            
        return {
            "collections": collections_count,
            "total_documents": sum(collections_count.values()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get data status: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Check if database has data and process raw_data if needed"""
    try:
        print("Starting up RuleBox F1 API...")
        db = processor.db
        collections = db.list_collection_names()
        
        # Check if we have any data
        total_documents = 0
        for collection_name in collections:
            if collection_name not in ['system.indexes', 'summary']:
                try:
                    count = db[collection_name].count_documents({})
                    total_documents += count
                except:
                    pass
        
        print(f"Found {total_documents} documents in database")
        
        # Only process if database is completely empty
        if total_documents == 0:
            print("Database is empty. Will process raw_data folder in background...")
            # Don't await - let it run in background
            asyncio.create_task(process_data_in_background())
        else:
            print(f"Database already contains {total_documents} documents - skipping data processing")
            
    except Exception as e:
        print(f"Startup check failed: {e}")

async def process_data_in_background():
    """Process data in background without blocking startup"""
    try:
        print("Background processing started...")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, processor.process_documents)
        print(f"Background data processing completed: {result}")
    except Exception as e:
        print(f"Background data processing failed: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)