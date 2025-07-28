from openai import AsyncOpenAI
from pymongo import MongoClient
import dotenv
import os
import asyncio

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    print(f"Warning: .env file not found at {dotenv_path}")
else:
    print(f"Loading .env file from {dotenv_path}")
dotenv.load_dotenv(dotenv_path=dotenv_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY is not set in the environment variables. AI features will be disabled.")
    ai_client = None
else:
    print(f"OPENROUTER_API_KEY loaded successfully: {OPENROUTER_API_KEY[:4]}...")
    try:
        ai_client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
    except Exception as e:
        print(f"Error initializing OpenAI client: {e}")
        ai_client = None


# MongoDB configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')  # Changed from MONGODB_URI
client = MongoClient(MONGODB_URL)  # Changed from MONGODB_URI

db = client.get_database("rulebox_f1_database")
rules_collection = db["rules"]
try:
    existing_indexes = rules_collection.index_information()
    if not any("text" in index.get("key", [{}])[0] for index in existing_indexes.values()):
        print("Creating text index on the 'rules' collection...")
        rules_collection.create_index(
            [("title", "text"), ("content", "text")],
            name="rules_text_index"
        )
        print("Text index created successfully.")
    else:
        print("Text index already exists on the 'rules' collection.")
except Exception as e:
    print(f"Error ensuring text index on 'rules' collection: {e}")

# Store conversation history in memory (in production, use Redis or database)
conversation_history = {}

async def ai_query(query, context_rules=None, conversation_id=None):  # Make it async
    if not ai_client:
        return "AI features are currently not available due to client initialization issues. Please check the OpenRouter API configuration."
    
    try:
        # Get conversation history if conversation_id is provided
        messages = []
        if conversation_id and conversation_id in conversation_history:
            messages = conversation_history[conversation_id]
        
        if not context_rules:
            if not client:
                return "Database connection is not available. Please provide a MongoDB URI."
            rules_collection = db["rules"]
            context_rules = list(rules_collection.find({"$text": {"$search": query}}).limit(3))
            if not context_rules:
                context_rules = []
        
        context = ""
        for rule in context_rules[:3]:
            context += f"Rule {rule['rule_id']}: {rule['title']}\n"
            context += f"Content: {rule['content'][:500]}...\n\n"
        
        # Build system message with context
        system_message = f"""You are an AI assistant specializing in Formula 1 regulations. 
Based on the following F1 regulations context, please answer questions accurately.

Context:
{context}

Please provide clear, accurate answers based on the regulations provided. If the regulations don't contain enough information to answer the question completely, please indicate what additional information might be needed."""
        
        # Add system message if this is the first message in conversation
        if not messages:
            messages.append({"role": "system", "content": system_message})
        
        # Add user query
        messages.append({"role": "user", "content": query})
        
        response = await ai_client.chat.completions.create(
            model="deepseek/deepseek-r1",
            messages=messages,
            max_tokens=1000,
            temperature=0.3
        )
        
        ai_response = response.choices[0].message.content
        
        # Add AI response to conversation history
        messages.append({"role": "assistant", "content": ai_response})
        
        # Store conversation history (keep last 10 messages to avoid token limits)
        if conversation_id:
            conversation_history[conversation_id] = messages[-10:]
        
        return ai_response
    except Exception as e:
        return f"AI query error: {e}"