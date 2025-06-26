from mcp.server.fastmcp import FastMCP
import json, os
import requests
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('.env')

# Initialize the MCP server
mcp = FastMCP("PRDGenerator", timeout=120000)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
API_ENDPOINT = "https://api.fireflies.ai/graphql"
API_KEY = FIREFLIES_API_KEY
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
# Define your GraphQL query
query = """
{
  transcripts {
    id
    date
    sentences{
    text
    }
  }
}
"""

# Structure your request data
data = {
    "query": query
}

response = requests.post(API_ENDPOINT, headers=headers, json=data)

# Global variable to store the latest transcript
latest_transcript_data = None

def get_latest_transcript_from_fireflies():
    response = requests.post(API_ENDPOINT, headers=headers, json=data)
    
    if response.status_code == 200:
        # Extract the transcript data from the response 
        latest_transcript = response.json().get('data').get('transcripts')[0]
        
        # Concatenate the sentences to form the full transcript text
        sentences = latest_transcript.get('sentences', [])
        full_transcript_text = " ".join(sentence['text'] for sentence in sentences)
        
        # Add the concatenated text to the latest_transcript dictionary
        latest_transcript['text'] = full_transcript_text
        return latest_transcript   
    else:
        print("Failed to fetch data from Fireflies. Status Code:", response.status_code)
        return None
# Tool to fetch the latest transcript from Fireflies
@mcp.tool()
def fetch_latest_transcript() -> dict:
    """
    Fetch the latest transcript from Fireflies
    
    Returns:
        The latest transcript data
    """
    global latest_transcript_data
    transcript_data = get_latest_transcript_from_fireflies()
    if transcript_data:
        # Store the transcript data in the global variable
        latest_transcript_data = transcript_data
        return {
            "id": transcript_data.get("id"),
            "date": transcript_data.get("date"),
            "text": transcript_data.get("text"),
            "status": "success"
        }
    else:
        return {
            "status": "error",
            "message": "Failed to fetch transcript from Fireflies"
        }

# Tool to generate a PRD from the latest fetched Fireflies transcript
@mcp.tool()
def generate_prd() -> dict:
    """
    Generate a PRD from the latest fetched Fireflies transcript
    
    Returns:
        A structured PRD document
    """
    global latest_transcript_data
    
    # Use the latest fetched transcript if available
    if latest_transcript_data and latest_transcript_data.get("text"):
        transcript_text = latest_transcript_data.get("text", "")
    else:
        # If no transcript is in memory, fetch a new one
        transcript_data = get_latest_transcript_from_fireflies()
        if transcript_data:
            transcript_text = transcript_data.get("text", "")
            # Update the global variable
            latest_transcript_data = transcript_data
        else:
            return {"error": "Failed to fetch transcript. Please run fetch_latest_transcript first."}
    
    # Generate PRD from the transcript text
    prd = analyze_and_generate_prd(transcript_text)
    
    return prd

# Helper function to analyze transcript and generate PRD
def analyze_and_generate_prd(transcript_text: str) -> dict:
    """
    Analyze the transcript and generate a structured PRD
    """
    prompt = f"""
    You are a helpful assistant that generates a Product Requirements Document (PRD) from a transcript.
    
    Please structure the PRD with the following sections:
    
    1. Introduction
    2. Goals
    3. Target Users
    4. User Stories
    5. Functional Requirements
    6. Non-Functional Requirements
    7. Technical Specifications
    8. Success Metrics
    9. Future Considerations (Out of Scope for V1)
    10. Risks and Assumptions

    Here is the transcript text:
    {transcript_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates a PRD from a transcript."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content
    

if __name__ == "__main__":
    import os
    host = os.getenv('MCP_HOST', '0.0.0.0')
    port = int(os.getenv('MCP_PORT', 8002))
    mcp.run(transport="http", host=host, port=port, path="/mcp")
