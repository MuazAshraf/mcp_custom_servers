from mcp.server.fastmcp import FastMCP
import json, os
import requests
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv('.env')

# Initialize the MCP server with stateless HTTP for FastAPI mounting
mcp = FastMCP("PRDGenerator", timeout=120000, stateless_http=True)
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
    
    Follow this EXACT structure with EXACT Headings for every PRD:
    1. Title & Metadata
    - Title: Clear, concise (e.g. "AI-Powered Resume Analyzer v1.0")
    - Author: Name, email
    - Date Created / Last Updated
    - Status: Draft / In Review / Final
    - Version: v0.1, v1.0, etc.

    2. Executive Summary
    - One-paragraph overview of the product or feature
    - Why are we building this?
    - Who is it for?
    - Example: “We're building an AI-powered resume analyzer to help job seekers optimize their resumes using real-time feedback.”

    3. Goals & Objectives
    - Primary Goal
    - Secondary Goals (if any)
    - Non-goals (what is out of scope)

    4. Problem Statement
    - What is the problem we're solving?
    - What pain points are we addressing?

    5. Success Metrics (KPIs)
    - Quantifiable results that define success
    - e.g. “90% of users complete resume analysis in under 2 minutes”

    6. Target Audience / Personas
    - Who are the users?
    - What are their needs, behaviors, and pain points?

    7. User Stories or Use Cases
    Format:
    - As a [user], I want to [do something], so that [benefit]
    - Example:
    As a job seeker, I want to upload my resume and receive improvement suggestions so that I can get more interview calls.

    8. Functional Requirements
    - List of specific features or behaviors:
    - Upload resume (PDF, DOCX)
    - Analyze text content with GPT
    - Highlight weaknesses and suggestions
    - Download improved resume

    9. Non-Functional Requirements
    - Performance: Response in < 3 sec
    - Security: GDPR-compliant
    - Scalability, Localization, Accessibility, etc.

    10. Wireframes / UI Mockups
    Include:
    - Landing Page
    - Upload Section
    - Results Page
    - Use Figma links, images, or embeds.

    11. Technical Considerations
    Tech stack
    - APIs to be used (e.g., OpenAI, Pinecone)
    - Integrations
    - Constraints (e.g., browser only, no mobile support)

    12. Risks & Assumptions
    - What are we assuming?
    - What could go wrong?

    13. Timeline / Milestones
    - Design: DD/MM – DD/MM
    - Development: DD/MM – DD/MM
    - Testing: DD/MM – DD/MM
    - Launch: DD/MM

    14. Appendices (Optional)
    - Links to research
    - References
    - Meeting notes
    - Competitive analysis

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
    mcp.run(transport="streamable-http")
