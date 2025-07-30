# Simple MCP Server Documentation

## Overview
The Simple MCP server is a minimal example server with a single "hello" tool for testing purposes.

## Configuration
No configuration required.

## Endpoints / Tools

### 1. hello
Say hello.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "hello",
  "arguments": {}
}
```

**Example Response:**
```
"Hello, world!"
```

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Say Hello
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "hello",
    "arguments": {}
  }'
```

## Notes
- This is a minimal example server for testing MCP server setup
- Useful for verifying that your MCP infrastructure is working correctly