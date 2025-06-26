from mcp.server.fastmcp import FastMCP
import json, os, hmac, hashlib
import requests
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv('.env')

# Initialize the MCP server with stateless HTTP for FastAPI mounting
mcp = FastMCP("FirefliesServer", timeout=120000, stateless_http=True)
FIREFLIES_API_KEY = os.getenv("FIREFLIES_API_KEY")
API_ENDPOINT = "https://api.fireflies.ai/graphql"

# Headers for Fireflies API requests
def get_headers():
    return {
        "Authorization": f"Bearer {FIREFLIES_API_KEY}",
        "Content-Type": "application/json"
    }

# Helper function to make GraphQL requests to Fireflies API
def fireflies_request(query: str, variables: Dict = None) -> Dict:
    """Make a GraphQL request to the Fireflies API"""
    try:
        data = {"query": query}
        if variables:
            data["variables"] = variables
            
        response = requests.post(API_ENDPOINT, headers=get_headers(), json=data)
        
        if response.status_code == 200:
            result = response.json()
            if "errors" in result:
                return {"error": f"GraphQL errors: {result['errors']}"}
            return result.get("data", {})
        else:
            return {"error": f"HTTP error: {response.status_code} - {response.text}"}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# ===== USER MANAGEMENT TOOLS =====

@mcp.tool()
def get_current_user() -> Dict:
    """
    Get current user details (the API key owner)
    
    Returns:
        Current user details including transcripts, permissions, and integrations
    """
    query = """
    {
        user {
            user_id
            name
            email
            num_transcripts
            recent_meeting
            minutes_consumed
            is_admin
            integrations
            user_groups {
                name
                handle
            }
        }
    }
    """
    return fireflies_request(query)

@mcp.tool()
def get_all_team_users() -> Dict:
    """
    Get list of all users in the team
    
    Returns:
        List of all team users with details
    """
    query = """
    {
        users {
            user_id
            email
            name
            num_transcripts
            recent_meeting
            minutes_consumed
            is_admin
            integrations
            user_groups {
                name
                handle
            }
        }
    }
    """
    return fireflies_request(query)

@mcp.tool()
def get_user_by_email(email: str) -> Dict:
    """
    Get user details by email (searches through team users)
    
    Args:
        email: User's email address
        
    Returns:
        User details if found
    """
    # First get all users, then filter by email
    users_result = fireflies_request("""
    {
        users {
            user_id
            email
            name
            num_transcripts
            recent_meeting
            minutes_consumed
            is_admin
            integrations
        }
    }
    """)
    
    if "error" in users_result:
        return users_result
    
    users = users_result.get("users", [])
    for user in users:
        if user.get("email", "").lower() == email.lower():
            return {"user": user}
    
    return {"error": f"User with email {email} not found"}

# ===== SIMPLE TRANSCRIPT TOOLS =====

@mcp.tool()
def get_my_recent_transcripts(limit: int = 10) -> Dict:
    """
    Get your recent transcripts (owned by you)
    
    Args:
        limit: Number of transcripts to return (default 10, max 50)
        
    Returns:
        List of your recent transcripts
    """
    query = """
    query GetMyTranscripts($limit: Int) {
        transcripts(mine: true, limit: $limit) {
            id
            title
            date
            duration
            organizer_email
            participants
            transcript_url
            audio_url
            video_url
            summary {
                keywords
                action_items
                overview
                short_summary
                meeting_type
            }
        }
    }
    """
    variables = {"limit": min(limit, 50)}
    return fireflies_request(query, variables)

@mcp.tool()
def get_latest_transcript() -> Dict:
    """
    Get the most recent transcript (yours)
    
    Returns:
        Latest transcript with full details
    """
    query = """
    {
        transcripts(mine: true, limit: 1) {
            id
            title
            date
            duration
            organizer_email
            participants
            transcript_url
            audio_url
            video_url
            summary {
                keywords
                action_items
                overview
                short_summary
                meeting_type
                topics_discussed
            }
        }
    }
    """
    result = fireflies_request(query)
    if "transcripts" in result and result["transcripts"]:
        return {"transcript": result["transcripts"][0]}
    return {"error": "No transcripts found"}

@mcp.tool()
def search_transcripts_by_title(title: str, limit: int = 10) -> Dict:
    """
    Search transcripts by title
    
    Args:
        title: Title to search for (partial match)
        limit: Number of results to return
        
    Returns:
        List of matching transcripts
    """
    query = """
    query SearchTranscripts($title: String, $limit: Int) {
        transcripts(title: $title, limit: $limit) {
            id
            title
            date
            duration
            organizer_email
            participants
            summary {
                overview
                short_summary
                meeting_type
            }
        }
    }
    """
    variables = {"title": title, "limit": limit}
    return fireflies_request(query, variables)

@mcp.tool()
def get_team_transcripts(limit: int = 10) -> Dict:
    """
    Get recent transcripts from your entire team
    
    Args:
        limit: Number of transcripts to return
        
    Returns:
        List of team transcripts
    """
    query = """
    query GetTeamTranscripts($limit: Int) {
        transcripts(limit: $limit) {
            id
            title
            date
            duration
            organizer_email
            participants
            user {
                name
                email
            }
            summary {
                overview
                meeting_type
            }
        }
    }
    """
    variables = {"limit": limit}
    return fireflies_request(query, variables)

@mcp.tool()
def get_transcript_full_details(transcript_id: str) -> Dict:
    """
    Get complete transcript details including sentences and analytics
    
    Args:
        transcript_id: ID of the transcript (get this from other transcript tools)
        
    Returns:
        Complete transcript data with all details
    """
    query = """
    query GetTranscript($transcriptId: String!) {
        transcript(id: $transcriptId) {
            id
            title
            date
            dateString
            duration
            organizer_email
            participants
            transcript_url
            audio_url
            video_url
            speakers {
                id
                name
            }
            sentences {
                index
                speaker_name
                speaker_id
                text
                start_time
                end_time
            }
            summary {
                keywords
                action_items
                outline
                overview
                short_summary
                meeting_type
                topics_discussed
            }
            analytics {
                sentiments {
                    negative_pct
                    neutral_pct
                    positive_pct
                }
                speakers {
                    speaker_id
                    name
                    duration
                    word_count
                    longest_monologue
                    filler_words
                    questions
                }
            }
        }
    }
    """
    variables = {"transcriptId": transcript_id}
    return fireflies_request(query, variables)

# ===== SIMPLE MANAGEMENT TOOLS =====

@mcp.tool()
def upload_audio_simple(url: str, title: str) -> Dict:
    """
    Upload audio/video file for transcription (simple version)
    
    Args:
        url: HTTPS URL of the media file (must be publicly accessible)
        title: Title for the meeting/transcript
        
    Returns:
        Upload status
    """
    query = """
    mutation UploadAudio($input: AudioUploadInput) {
        uploadAudio(input: $input) {
            success
            title
            message
        }
    }
    """
    variables = {
        "input": {
            "url": url,
            "title": title
        }
    }
    return fireflies_request(query, variables)

@mcp.tool()
def add_bot_to_meeting(meeting_link: str, title: str = None) -> Dict:
    """
    Add Fireflies bot to an ongoing meeting (simple version)
    
    Args:
        meeting_link: Meeting URL (Google Meet, Zoom, etc.)
        title: Optional meeting title
        
    Returns:
        Success status
    """
    query = """
    mutation AddToLiveMeeting($meetingLink: String!, $title: String) {
        addToLiveMeeting(meeting_link: $meetingLink, title: $title) {
            success
        }
    }
    """
    variables = {"meetingLink": meeting_link}
    if title:
        variables["title"] = title
    
    return fireflies_request(query, variables)

@mcp.tool()
def update_transcript_title(transcript_id: str, new_title: str) -> Dict:
    """
    Update meeting title - Admin privileges required
    
    Args:
        transcript_id: ID of the transcript to update
        new_title: New title for the meeting
        
    Returns:
        Updated transcript info
    """
    query = """
    mutation UpdateMeetingTitle($input: UpdateMeetingTitleInput!) {
        updateMeetingTitle(input: $input) {
            title
        }
    }
    """
    variables = {
        "input": {
            "id": transcript_id,
            "title": new_title
        }
    }
    return fireflies_request(query, variables)

@mcp.tool()
def delete_transcript_by_id(transcript_id: str) -> Dict:
    """
    Delete a transcript - Admin privileges required
    
    Args:
        transcript_id: ID of the transcript to delete
        
    Returns:
        Deleted transcript information
    """
    query = """
    mutation DeleteTranscript($transcriptId: String!) {
        deleteTranscript(id: $transcriptId) {
            id
            title
            date
            duration
            organizer_email
        }
    }
    """
    variables = {"transcriptId": transcript_id}
    return fireflies_request(query, variables)

@mcp.tool()
def get_team_analytics_simple() -> Dict:
    """
    Get team analytics (Business+ plan required)
    
    Returns:
        Team analytics with conversation metrics
    """
    query = """
    {
        analytics {
            team {
                conversation {
                    total_meetings_count
                    total_meeting_notes_count
                    teammates_count
                    average_filler_words
                    average_questions
                    average_sentiments {
                        negative_pct
                        neutral_pct
                        positive_pct
                    }
                    average_words_per_minute
                }
                meeting {
                    count
                    duration
                    average_count
                    average_duration
                }
            }
        }
    }
    """
    return fireflies_request(query)

# This server is now mounted in main.py FastAPI hub
# Individual server mode is disabled in favor of FastAPI mounting
