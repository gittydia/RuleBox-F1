from openai import OpenAI
from pymongo import MongoClient
import dotenv
import os
import asyncio  # Add asyncio import for handling CancelledError

# Explicitly load the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if not os.path.exists(dotenv_path):
    print(f"Warning: .env file not found at {dotenv_path}")
else:
    print(f"Loading .env file from {dotenv_path}")
dotenv.load_dotenv(dotenv_path=dotenv_path)

# Retrieve OpenRouter API key from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    print("Warning: OPENROUTER_API_KEY is not set in the environment variables. AI features will be disabled.")
    ai_client = None
else:
    print(f"OPENROUTER_API_KEY loaded successfully: {OPENROUTER_API_KEY[:4]}...")  # Debug print
    # Initialize OpenRouter client
    ai_client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )

# Initialize MongoDB client with a hardcoded URI
MONGODB_URI = "mongodb://localhost:27017/"
print(f"Using hardcoded MongoDB URI: {MONGODB_URI}")  # Debug print

# Initialize MongoDB client
db_client = MongoClient(MONGODB_URI)
db = db_client.get_database("rulebox_f1_database")  # Using rulebox_f1_database

# Ensure text index exists on the "rules" collection
rules_collection = db["rules"]  # Replace "rules" with your collection name
try:
    # Check if a text index already exists
    existing_indexes = rules_collection.index_information()
    if not any("text" in index.get("key", [{}])[0] for index in existing_indexes.values()):
        print("Creating text index on the 'rules' collection...")
        rules_collection.create_index(
            [("title", "text"), ("content", "text")],  # Replace with fields to index
            name="rules_text_index"
        )
        print("Text index created successfully.")
    else:
        print("Text index already exists on the 'rules' collection.")
except Exception as e:
    print(f"Error ensuring text index on 'rules' collection: {e}")

def ai_query(ai_client, query, context_rules=None):
    """Query AI with context from relevant rules"""
    if not ai_client:
        return "AI features are not available. Please provide an OpenRouter API key."

    try:
        # Automatically fetch relevant rules from MongoDB based on the query if context_rules is not provided
        if not context_rules:
            if not db_client:
                return "Database connection is not available. Please provide a MongoDB URI."
            
            rules_collection = db["rules"]  # Replace "rules" with your collection name
            # Perform a search in the database for rules relevant to the query
            context_rules = list(rules_collection.find({"$text": {"$search": query}}).limit(3))

            if not context_rules:
                return "No relevant context rules found in the database for the given query."

        # Build context
        context = ""
        for rule in context_rules[:3]:  # Limit context to avoid token limits
            context += f"Rule {rule['rule_id']}: {rule['title']}\n"
            context += f"Content: {rule['content'][:500]}...\n\n"

        # Create prompt
        prompt = f"""Based on the following F1 regulations context, please answer the question.

Context:
{context}

Question: {query}

Please provide a clear, accurate answer based on the regulations provided. If the regulations don't contain enough information to answer the question completely, please indicate what additional information might be needed."""

        # Query OpenRouter
        response = ai_client.chat.completions.create(
            model="deepseek/deepseek-r1",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.3
        )

        return response.choices[0].message.content

    except asyncio.exceptions.CancelledError:
        return "The operation was cancelled. Please try again."
    except Exception as e:
        return f"AI query error: {e}"
