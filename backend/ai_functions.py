from openai import AsyncOpenAI
from pymongo import MongoClient
import dotenv
import os
import asyncio
from fastapi import HTTPException

# Load .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    print(f"Warning: .env file not found at {dotenv_path}")
else:
    print(f"Loading .env file from {dotenv_path}")
dotenv.load_dotenv(dotenv_path=dotenv_path)

# API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY is not set.")
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

# MongoDB setup
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
client = MongoClient(MONGODB_URL)
db = client.get_database("rulebox_f1_database")
rules_collection = db["rules"]

# Create index if needed
try:
    existing_indexes = rules_collection.index_information()
    if not any("text" in index.get("key", [{}])[0] for index in existing_indexes.values()):
        print("Creating text index...")
        rules_collection.create_index(
            [("title", "text"), ("content", "text")],
            name="rules_text_index"
        )
        print("Index created.")
    else:
        print("Text index already exists.")
except Exception as e:
    print(f"Index error: {e}")

# In-memory conversation history
conversation_history = {}

# Main AI query function
async def ai_query(query, context_rules=None, conversation_id=None):
    if not ai_client:
        raise HTTPException(status_code=503, detail="AI features unavailable. Check OpenRouter API key.")

    try:
        # Previous messages
        messages = []
        if conversation_id and conversation_id in conversation_history:
            messages = conversation_history[conversation_id]

        # Search context if not provided
        if not context_rules:
            context_rules = list(rules_collection.find({"$text": {"$search": query}}).limit(3))

        has_context = bool(context_rules)

        # Build system message
        if has_context:
            context = ""
            for rule in context_rules[:3]:
                context += f"- {rule.get('title', '')}: {rule.get('content', '')[:100]}...\n"
            system_message = f"""You are a world-class Formula 1 expert AI. Use the regulation context below if helpful, but rely primarily on your own expert knowledge.

Regulation Context:
{context}
"""
        else:
            system_message = """You are a world-class Formula 1 expert. You MUST answer all questions using your own extensive F1 knowledge.

NEVER say "context is missing" — you know all F1 rules, procedures, teams, and penalties.

Example:
Q: What does a black flag mean?
A: A black flag means the driver is disqualified and must return to the pits immediately. It is used for serious infractions or dangerous driving.
"""

        # Build chat messages
        if not messages:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": query})

        response = await ai_client.chat.completions.create(
            model="deepseek/deepseek-r1",  # DeepSeek R1 model
            messages=messages[-2],
            max_tokens=50,  
            temperature=0.1
        )

        # Validate response structure
        if not response or not response.choices:
            raise HTTPException(status_code=500, detail="Invalid response from AI client.")

        ai_response = response.choices[0].message.content

        # Update history
        messages.append({"role": "assistant", "content": ai_response})
        if conversation_id:
            conversation_history[conversation_id] = messages[-10:]

        return {"response": ai_response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI query error: {e}")
