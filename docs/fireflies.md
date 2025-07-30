# Fireflies MCP Server Documentation

## Overview
The Fireflies MCP server provides tools for interacting with Fireflies.ai, a meeting transcription and analysis service. It allows you to manage users, transcripts, and upload audio/video files for transcription.

## Configuration
Set the following environment variable in `.env`:

```bash
FIREFLIES_API_KEY=your-fireflies-api-key
```

## Endpoints / Tools

### User Management Tools

#### 1. get_current_user
Get current user details (the API key owner).

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_current_user",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "user": {
    "user_id": "123456",
    "name": "John Doe",
    "email": "john@example.com",
    "num_transcripts": 150,
    "recent_meeting": "2024-01-15",
    "minutes_consumed": 5000,
    "is_admin": true,
    "integrations": ["zoom", "google"],
    "user_groups": [
      {
        "name": "Engineering",
        "handle": "engineering"
      }
    ]
  }
}
```

#### 2. get_all_team_users
Get list of all users in the team.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_all_team_users",
  "arguments": {}
}
```

#### 3. get_user_by_email
Get user details by email (searches through team users).

**Parameters:**
- `email` (string, required): User's email address

**Example Request:**
```json
{
  "tool_name": "get_user_by_email",
  "arguments": {
    "email": "john@example.com"
  }
}
```

### Transcript Tools

#### 4. get_my_recent_transcripts
Get your recent transcripts (owned by you).

**Parameters:**
- `limit` (integer, optional): Number of transcripts to return (default 10, max 50)

**Example Request:**
```json
{
  "tool_name": "get_my_recent_transcripts",
  "arguments": {
    "limit": 20
  }
}
```

#### 5. get_latest_transcript
Get the most recent transcript (yours).

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_latest_transcript",
  "arguments": {}
}
```

#### 6. search_transcripts_by_title
Search transcripts by title.

**Parameters:**
- `title` (string, required): Title to search for (partial match)
- `limit` (integer, optional): Number of results to return

**Example Request:**
```json
{
  "tool_name": "search_transcripts_by_title",
  "arguments": {
    "title": "Product Meeting",
    "limit": 5
  }
}
```

#### 7. get_team_transcripts
Get recent transcripts from your entire team.

**Parameters:**
- `limit` (integer, optional): Number of transcripts to return

**Example Request:**
```json
{
  "tool_name": "get_team_transcripts",
  "arguments": {
    "limit": 15
  }
}
```

#### 8. get_transcript_full_details
Get complete transcript details including sentences and analytics.

**Parameters:**
- `transcript_id` (string, required): ID of the transcript

**Example Request:**
```json
{
  "tool_name": "get_transcript_full_details",
  "arguments": {
    "transcript_id": "abc123def456"
  }
}
```

**Example Response (partial):**
```json
{
  "transcript": {
    "id": "abc123def456",
    "title": "Product Review Meeting",
    "date": "2024-01-15T10:00:00Z",
    "duration": 3600,
    "participants": ["john@example.com", "jane@example.com"],
    "summary": {
      "keywords": ["product", "launch", "timeline"],
      "action_items": ["Review design mockups", "Schedule QA testing"],
      "overview": "Discussion about Q1 product launch...",
      "meeting_type": "internal_meeting"
    },
    "analytics": {
      "sentiments": {
        "positive_pct": 65,
        "neutral_pct": 30,
        "negative_pct": 5
      },
      "speakers": [
        {
          "name": "John Doe",
          "duration": 1800,
          "word_count": 2500,
          "questions": 15
        }
      ]
    }
  }
}
```

### Management Tools

#### 9. upload_audio_simple
Upload audio/video file for transcription.

**Parameters:**
- `url` (string, required): HTTPS URL of the media file (must be publicly accessible)
- `title` (string, required): Title for the meeting/transcript

**Example Request:**
```json
{
  "tool_name": "upload_audio_simple",
  "arguments": {
    "url": "https://example.com/meeting-recording.mp4",
    "title": "Q1 Planning Meeting"
  }
}
```

#### 10. add_bot_to_meeting
Add Fireflies bot to an ongoing meeting.

**Parameters:**
- `meeting_link` (string, required): Meeting URL (Google Meet, Zoom, etc.)
- `title` (string, optional): Optional meeting title

**Example Request:**
```json
{
  "tool_name": "add_bot_to_meeting",
  "arguments": {
    "meeting_link": "https://meet.google.com/abc-defg-hij",
    "title": "Daily Standup"
  }
}
```

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Get Current User
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_current_user",
    "arguments": {}
  }'
```

### Example: Search Transcripts
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_transcripts_by_title",
    "arguments": {
      "title": "Weekly",
      "limit": 10
    }
  }'
```

### Example: Upload Audio
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "upload_audio_simple",
    "arguments": {
      "url": "https://example.com/recording.mp3",
      "title": "Customer Call Recording"
    }
  }'
```

## Notes
- The Fireflies API uses GraphQL internally, but the MCP server provides simple REST-like tools
- Audio/video files for upload must be publicly accessible via HTTPS
- Transcript IDs are required for detailed transcript retrieval - get them from listing tools first
- Meeting types include: internal_meeting, external_meeting, interview, sales_call, etc.
- Analytics include sentiment analysis, speaker statistics, and conversation metrics