# Mailgun MCP Server Documentation

## Overview
The Mailgun MCP server provides tools for managing multiple Mailgun accounts and sending emails through the Mailgun API.

## Configuration
Configure accounts using environment variables in `.env`:

```bash
# Option 1: JSON format (recommended)
MAILGUN_ACCOUNTS='{"account_name": {"api_key": "your-api-key", "domain": "your-domain.com"}}'

# Option 2: Individual environment variables
MAILGUN_ACCOUNT_1_NAME=account1
MAILGUN_ACCOUNT_1_KEY=your-api-key
MAILGUN_ACCOUNT_1_DOMAIN=your-domain.com
```

## Endpoints / Tools

### 1. list_accounts
List all configured Mailgun accounts.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "list_accounts",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "accounts": [
    {
      "name": "projectwe",
      "domain": "projectwe.com",
      "is_current": true
    }
  ],
  "total": 1
}
```

### 2. switch_account
Switch to a different Mailgun account.

**Parameters:**
- `account_name` (string, required): Name of the account to switch to

**Example Request:**
```json
{
  "tool_name": "switch_account",
  "arguments": {
    "account_name": "projectwe"
  }
}
```

### 3. get_current_account
Get the currently active Mailgun account.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_current_account",
  "arguments": {}
}
```

### 4. send_email
Send an email using the current Mailgun account.

**Parameters:**
- `to` (string, required): Recipient email address
- `subject` (string, required): Email subject
- `text` (string, required): Plain text body of the email
- `html` (string, optional): HTML body of the email
- `from_email` (string, optional): Sender email address (defaults to `noreply@{domain}`)

**Example Request:**
```json
{
  "tool_name": "send_email",
  "arguments": {
    "to": "muazashraf456@gmail.com",
    "subject": "Test Email",
    "text": "This is a plain text email.",
    "html": "<h1>Test Email</h1><p>This is an HTML email.</p> OPTIONAL PARAM", 
    "from_email": "projectwe@projectwe.com"
  }
}
```

### 5. get_domains
Get all domains for the current Mailgun account.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_domains",
  "arguments": {}
}
```

### 6. get_stats
Get email statistics for the current account.

**Parameters:**
- `event` (string, optional): Event type (default: "delivered")
- `duration` (string, optional): Duration (default: "7d")

**Available Event Types:**
- `accepted`: Messages accepted by Mailgun
- `delivered`: Messages successfully delivered
- `failed`: Messages that failed (temporary or permanent)
- `opened`: Messages that were opened
- `clicked`: Messages with clicked links
- `unsubscribed`: Recipients who unsubscribed
- `complained`: Recipients who marked as spam
- `stored`: Messages stored for later retrieval

**Available Durations:**
- `1d`: Last 24 hours
- `7d`: Last 7 days
- `30d`: Last 30 days

**Example Request:**
```json
{
  "tool_name": "get_stats",
  "arguments": {
    "event": "delivered",
    "duration": "30d"
  }
}
```

### 7. get_events
Get recent events for the current account.

**Parameters:**
- `limit` (integer, optional): Number of events to retrieve (1-300, default: 25)
- `event` (string, optional): Filter by event type

**Available Event Types for Filtering:**
- `accepted`
- `delivered`
- `failed`
- `opened`
- `clicked`
- `unsubscribed`
- `complained`
- `stored`
- `rejected`
- `list_member_uploaded`
- `list_member_upload_error`
- `list_uploaded`

**Example Request:**
```json
{
  "tool_name": "get_events",
  "arguments": {
    "limit": 50,
    "event": "delivered"
  }
}
```

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Send Email
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "send_email",
    "arguments": {
      "to": "test@example.com",
      "subject": "Test from Mailgun MCP",
      "text": "This is a test email.",
      "from_email": "noreply@projectwe.com"
    }
  }'
```

### Example: Get Statistics
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_stats",
    "arguments": {
      "event": "delivered",
      "duration": "7d"
    }
  }'
```

## Notes
- The `from_email` domain must match your Mailgun domain
- Rate limits apply based on your Mailgun plan
- All timestamps in responses are in UTC
- Events are retained for 30 days in Mailgun