import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from pinecone import Pinecone
import sys

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

def generate_embedding(text):
    """Generate embedding for a given text using OpenAI's text-embedding-3-large"""
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

def prepare_readme_for_pinecone():
    """Read readme.md and prepare it for Pinecone with embeddings"""
    # Read the readme file
    with open("readme.md", "r") as f:
        content = f.read()
    
    # Generate embedding
    print("Generating embedding for readme.md...")
    embedding = generate_embedding(content)
    
    # Prepare the record for Pinecone
    record = {
        "id": "readme-md",
        "values": embedding,
        "metadata": {
            "text": content[:1000],  # Store first 1000 chars as metadata (Pinecone limit)
            "filename": "readme.md",
            "doc_type": "documentation",
            "full_text_length": len(content)
        }
    }
    
    # Save to a JSON file for reference
    with open("readme_embedding.json", "w") as f:
        json.dump({
            "record": record,
            "embedding_dimension": len(embedding),
            "model_used": "text-embedding-3-large"
        }, f, indent=2)
    
    print(f"Embedding generated successfully!")
    print(f"Dimension: {len(embedding)}")
    print(f"Record saved to readme_embedding.json")
    
    return record

if __name__ == "__main__":
    record = prepare_readme_for_pinecone()
    print("\nYou can now use this record with Pinecone's upsert-records tool")