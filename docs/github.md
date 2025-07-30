# GitHub MCP Server Documentation

## Overview
The GitHub MCP server provides tools for interacting with GitHub repositories, issues, pull requests, and more through the GitHub API.

## Configuration
Set the following environment variables in `.env`:

```bash
GITHUB_TOKEN=your-github-personal-access-token
OPENAI_API_KEY=your-openai-api-key  # Optional, for AI features
```

## Endpoints / Tools

### 1. create_repository
Create a new GitHub repository.

**Parameters:**
- `name` (string, required): Repository name
- `description` (string, optional): Repository description
- `private` (boolean, optional): Whether the repository is private (default: false)
- `auto_init` (boolean, optional): Initialize with README (default: true)

**Example Request:**
```json
{
  "tool_name": "create_repository",
  "arguments": {
    "name": "my-new-repo",
    "description": "A test repository",
    "private": false,
    "auto_init": true
  }
}
```

### 2. list_repositories
List user repositories.

**Parameters:**
- `username` (string, optional): Username to list repos for (default: authenticated user)
- `repo_type` (string, optional): Type of repos to list ("owner", "member", "all", default: "owner")

**Example Request:**
```json
{
  "tool_name": "list_repositories",
  "arguments": {
    "username": "octocat",
    "repo_type": "owner"
  }
}
```

### 3. create_issue
Create an issue in a repository.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `title` (string, required): Issue title
- `body` (string, optional): Issue body/description
- `labels` (array of strings, optional): Labels to apply

**Example Request:**
```json
{
  "tool_name": "create_issue",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "title": "Bug: Login not working",
    "body": "Users cannot login with valid credentials",
    "labels": ["bug", "high-priority"]
  }
}
```

### 4. list_issues
List repository issues.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `state` (string, optional): Issue state ("open", "closed", "all", default: "open")
- `labels` (string, optional): Comma-separated list of labels to filter by

**Example Request:**
```json
{
  "tool_name": "list_issues",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "state": "open",
    "labels": "bug,help-wanted"
  }
}
```

### 5. create_pull_request
Create a pull request.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `title` (string, required): PR title
- `head` (string, required): Branch containing changes
- `base` (string, optional): Base branch (default: "main")
- `body` (string, optional): PR description

**Example Request:**
```json
{
  "tool_name": "create_pull_request",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "title": "Add new feature",
    "head": "feature-branch",
    "base": "main",
    "body": "This PR adds the new login feature"
  }
}
```

### 6. upload_file
Upload or update a file in repository.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `path` (string, required): File path in repository
- `content` (string, required): File content
- `message` (string, required): Commit message
- `branch` (string, optional): Target branch (default: "main")

**Example Request:**
```json
{
  "tool_name": "upload_file",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "path": "docs/readme.md",
    "content": "# My Project\nThis is the readme file.",
    "message": "Add readme documentation",
    "branch": "main"
  }
}
```

### 7. search_code
Search code across GitHub.

**Parameters:**
- `query` (string, required): Search query
- `language` (string, optional): Programming language filter
- `repo` (string, optional): Specific repository to search in

**Example Request:**
```json
{
  "tool_name": "search_code",
  "arguments": {
    "query": "async function fetchData",
    "language": "javascript",
    "repo": "facebook/react"
  }
}
```

### 8. get_user_info
Get current GitHub user information.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_user_info",
  "arguments": {}
}
```

### 9. get_issue_details
Get detailed information about a specific issue.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `issue_number` (integer, required): Issue number

**Example Request:**
```json
{
  "tool_name": "get_issue_details",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "issue_number": 42
  }
}
```

### 10. get_issue_comments
Get all comments for a specific issue.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `issue_number` (integer, required): Issue number

**Example Request:**
```json
{
  "tool_name": "get_issue_comments",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "issue_number": 42
  }
}
```

### 11. create_issue_comment
Add a comment to an issue.

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name
- `issue_number` (integer, required): Issue number
- `body` (string, required): Comment text

**Example Request:**
```json
{
  "tool_name": "create_issue_comment",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo",
    "issue_number": 42,
    "body": "Thanks for reporting this issue. We'll look into it."
  }
}
```

### 12. respond_to_help_request
Auto-respond to latest /help comment in any issue (AI-powered).

**Parameters:**
- `owner` (string, required): Repository owner
- `repo` (string, required): Repository name

**Example Request:**
```json
{
  "tool_name": "respond_to_help_request",
  "arguments": {
    "owner": "myusername",
    "repo": "my-repo"
  }
}
```

## Resources
The server also provides MCP resources:
- `github://user/profile` - Get current user profile
- `github://repositories/recent` - Get recently updated repositories

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Create Issue
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_issue",
    "arguments": {
      "owner": "myusername",
      "repo": "test-repo",
      "title": "Test Issue from MCP",
      "body": "This is a test issue created via the GitHub MCP server"
    }
  }'
```

### Example: Search Code
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_code",
    "arguments": {
      "query": "useState",
      "language": "javascript"
    }
  }'
```

## Notes
- Requires a GitHub Personal Access Token with appropriate permissions
- Rate limits apply based on GitHub API limits (5000 requests/hour for authenticated requests)
- Some operations require specific repository permissions
- The AI-powered features require an OpenAI API key