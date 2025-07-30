# PRD Generator MCP Server Documentation

## Overview
The PRD (Product Requirements Document) Generator MCP server integrates with Fireflies.ai to fetch meeting transcripts and uses OpenAI to generate structured PRD documents from those transcripts.

## Configuration
Set the following environment variables in `.env`:

```bash
OPENAI_API_KEY=your-openai-api-key
FIREFLIES_API_KEY=your-fireflies-api-key
```

## Endpoints / Tools

### 1. fetch_latest_transcript
Fetch the latest transcript from Fireflies.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "fetch_latest_transcript",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "id": "abc123def456",
  "date": "2024-01-15T10:00:00Z",
  "text": "Full transcript text from the meeting...",
  "status": "success"
}
```

### 2. generate_prd
Generate a PRD from the latest fetched Fireflies transcript.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "generate_prd",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "status": "success",
  "prd": {
    "title": "Product Requirements Document",
    "sections": {
      "executive_summary": "...",
      "objectives": "...",
      "scope": "...",
      "requirements": "...",
      "success_criteria": "..."
    }
  }
}
```

## Workflow

1. **Fetch Transcript**: First, use `fetch_latest_transcript` to retrieve the most recent meeting transcript from Fireflies
2. **Generate PRD**: Then use `generate_prd` to create a structured PRD document from that transcript

The server maintains the latest transcript in memory, so you don't need to fetch it again before generating the PRD unless you want a newer transcript.

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Fetch Latest Transcript
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "fetch_latest_transcript",
    "arguments": {}
  }'
```

### Example: Generate PRD
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "generate_prd",
    "arguments": {}
  }'
```

## Notes
- The server has a 120-second timeout for operations due to potentially long AI processing times
- The PRD generation uses OpenAI's GPT model to analyze the transcript and create structured documentation
- If no transcript is in memory when calling `generate_prd`, it will automatically fetch the latest one
- The generated PRD includes standard sections like executive summary, objectives, scope, requirements, and success criteria