#!/usr/bin/env python3
"""
GitHub Action MCP Server
AI models ke liye GitHub integration
"""

import asyncio
import json
import os
import base64
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import ssl

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import AsyncOpenAI

# Load environment variables from .env file
script_dir = Path(__file__).parent
env_path = script_dir / '.env'
load_dotenv(env_path)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("github-mcp-server")

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN environment variable is required")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Create FastMCP server
mcp = FastMCP("github-mcp")

async def get_github_session():
    """Get or create GitHub API session"""
    return aiohttp.ClientSession()

async def github_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Make authenticated GitHub API request"""
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "GitHub-MCP-Server"
    }
    
    url = f"https://api.github.com/{endpoint.lstrip('/')}"
    
    # Create SSL context that's more permissive
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.request(method, url, headers=headers, json=data) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"GitHub API error {response.status}: {error_text}")
            
            return await response.json()

@mcp.tool()
async def create_repository(name: str, description: str = "", private: bool = False, auto_init: bool = True) -> str:
    """Create a new GitHub repository"""
    data = {
        "name": name,
        "description": description,
        "private": private,
        "auto_init": auto_init
    }
    
    result = await github_request("POST", "/user/repos", data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def list_repositories(username: str = "", repo_type: str = "owner") -> str:
    """List user repositories"""
    if username:
        endpoint = f"/users/{username}/repos"
    else:
        endpoint = f"/user/repos?type={repo_type}"
    
    repos = await github_request("GET", endpoint)
    
    result = {
        "total_count": len(repos),
        "repositories": [
            {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "description": repo["description"],
                "private": repo["private"],
                "html_url": repo["html_url"],
                "created_at": repo["created_at"],
                "updated_at": repo["updated_at"],
                "language": repo["language"],
                "stargazers_count": repo["stargazers_count"]
            }
            for repo in repos[:20]  # Limit to 20 for readability
        ]
    }
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_issue(owner: str, repo: str, title: str, body: str = "", labels: List[str] = None) -> str:
    """Create an issue in a repository"""
    if labels is None:
        labels = []
        
    data = {
        "title": title,
        "body": body,
        "labels": labels
    }
    
    result = await github_request("POST", f"/repos/{owner}/{repo}/issues", data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def list_issues(owner: str, repo: str, state: str = "open", labels: str = "") -> str:
    """List repository issues"""
    endpoint = f"/repos/{owner}/{repo}/issues?state={state}"
    if labels:
        endpoint += f"&labels={labels}"
    
    issues = await github_request("GET", endpoint)
    
    result = {
        "total_count": len(issues),
        "issues": [
            {
                "number": issue["number"],
                "title": issue["title"],
                "body": issue["body"][:200] + "..." if len(issue["body"]) > 200 else issue["body"],
                "state": issue["state"],
                "user": issue["user"]["login"],
                "created_at": issue["created_at"],
                "html_url": issue["html_url"]
            }
            for issue in issues[:10]
        ]
    }
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_pull_request(owner: str, repo: str, title: str, head: str, base: str = "main", body: str = "") -> str:
    """Create a pull request"""
    data = {
        "title": title,
        "body": body,
        "head": head,
        "base": base
    }
    
    result = await github_request("POST", f"/repos/{owner}/{repo}/pulls", data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def upload_file(owner: str, repo: str, path: str, content: str, message: str, branch: str = "main") -> str:
    """Upload or update a file in repository"""
    # Check if file exists to get SHA for update
    try:
        existing = await github_request("GET", f"/repos/{owner}/{repo}/contents/{path}?ref={branch}")
        sha = existing["sha"]
    except:
        sha = None
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": branch
    }
    
    if sha:
        data["sha"] = sha
    
    result = await github_request("PUT", f"/repos/{owner}/{repo}/contents/{path}", data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def search_code(query: str, language: str = "", repo: str = "") -> str:
    """Search code across GitHub"""
    search_query = query
    if language:
        search_query += f" language:{language}"
    if repo:
        search_query += f" repo:{repo}"
    
    results = await github_request("GET", f"/search/code?q={search_query}")
    
    result = {
        "total_count": results["total_count"],
        "items": [
            {
                "name": item["name"],
                "path": item["path"],
                "repository": item["repository"]["full_name"],
                "html_url": item["html_url"],
                "score": item["score"]
            }
            for item in results["items"][:10]
        ]
    }
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_user_info() -> str:
    """Get current GitHub user information"""
    result = await github_request("GET", "/user")
    return json.dumps(result, indent=2)

@mcp.resource("github://user/profile")
async def get_user_profile() -> str:
    """Get current GitHub user profile"""
    result = await github_request("GET", "/user")
    return json.dumps(result, indent=2)

@mcp.resource("github://repositories/recent")
async def get_recent_repositories() -> str:
    """Get recently updated repositories"""
    repos = await github_request("GET", "/user/repos?sort=updated&per_page=10")
    return json.dumps({"repositories": repos}, indent=2)

@mcp.tool()
async def get_issue_comments(owner: str, repo: str, issue_number: int) -> str:
    """Get all comments for a specific issue"""
    comments = await github_request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}/comments")
    
    result = {
        "issue_number": issue_number,
        "total_comments": len(comments),
        "comments": [
            {
                "id": comment["id"],
                "user": comment["user"]["login"],
                "body": comment["body"],
                "created_at": comment["created_at"],
                "updated_at": comment["updated_at"],
                "html_url": comment["html_url"]
            }
            for comment in comments
        ]
    }
    
    return json.dumps(result, indent=2)

@mcp.tool()
async def create_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> str:
    """Add a comment to an issue"""
    data = {
        "body": body
    }
    
    result = await github_request("POST", f"/repos/{owner}/{repo}/issues/{issue_number}/comments", data)
    return json.dumps(result, indent=2)

@mcp.tool()
async def get_issue_details(owner: str, repo: str, issue_number: int) -> str:
    """Get detailed information about a specific issue including comments count"""
    try:
        issue = await github_request("GET", f"/repos/{owner}/{repo}/issues/{issue_number}")
        
        result = {
            "number": issue["number"],
            "title": issue["title"],
            "body": issue["body"] or "",
            "state": issue["state"],
            "user": issue["user"]["login"],
            "assignees": [assignee["login"] for assignee in issue["assignees"]],
            "labels": [label["name"] for label in issue["labels"]],
            "comments_count": issue["comments"],
            "created_at": issue["created_at"],
            "updated_at": issue["updated_at"],
            "html_url": issue["html_url"]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting issue details: {e}")
        return json.dumps({
            "error": f"Could not fetch issue #{issue_number} from {owner}/{repo}",
            "details": str(e)
        }, indent=2)

@mcp.tool()
async def respond_to_help_request(owner: str, repo: str) -> str:
    """Auto-respond to latest /help comment in any issue"""
    
    try:
        # Get all open issues
        issues = await github_request("GET", f"/repos/{owner}/{repo}/issues?state=open&per_page=20")
        
        # Look for latest /help comment across all issues
        latest_help_comment = None
        target_issue = None
        
        for issue in issues:
            # Get comments for this issue
            comments = await github_request("GET", f"/repos/{owner}/{repo}/issues/{issue['number']}/comments")
            
            # Check each comment for /help trigger
            for comment in reversed(comments):  # Start from latest
                if "/help" in comment["body"].lower():
                    latest_help_comment = comment
                    target_issue = issue
                    break
            
            if latest_help_comment:
                break
        
        if not latest_help_comment:
            return json.dumps({
                "message": "No /help comments found in recent issues",
                "suggestion": "Ask someone to comment '/help' in an issue"
            }, indent=2)
        
        # Get repository context (codebase analysis)
        repo_context = await _get_repository_context(owner, repo)
        
        # Generate AI response using OpenAI
        ai_response = await _generate_smart_help_response(
            target_issue, latest_help_comment, repo_context
        )
        
        # Post response
        response_text = f"""🤖 **AI Assistant**

{ai_response}

---
**Codebase:** {repo_context.get('primary_language', 'Unknown')} • Files: {', '.join(repo_context.get('files', [])[:3])}

*AI-generated response. Verify code suggestions before use.*
"""
        
        result = await create_issue_comment(owner, repo, target_issue['number'], response_text)
        
        return json.dumps({
            "success": True,
            "responded_to_issue": target_issue['number'],
            "issue_title": target_issue['title'],
            "user_question": latest_help_comment['body'][:100] + "...",
            "response_preview": ai_response[:150] + "..."
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Error responding to help: {e}")
        return json.dumps({
            "error": f"Failed to respond: {str(e)}",
            "repository": f"{owner}/{repo}"
        }, indent=2)

async def _generate_smart_help_response(issue: dict, help_comment: dict, repo_context: dict) -> str:
    """Generate smart AI response using OpenAI"""
    
    # Create context for AI
    context = f"""
REPOSITORY: {repo_context.get('description', 'No description')}
LANGUAGE: {repo_context.get('primary_language', 'Unknown')}
KEY FILES: {', '.join(repo_context.get('files', [])[:8])}

ISSUE TITLE: {issue['title']}
ISSUE DESCRIPTION: {issue['body'][:800]}

USER HELP REQUEST: {help_comment['body']}
USER: @{help_comment['user']['login']}

README CONTEXT: {repo_context.get('readme_snippet', 'No README')[:600]}
"""

    try:
        if OPENAI_API_KEY:
            client = AsyncOpenAI(api_key=OPENAI_API_KEY)
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful coding assistant. A user asked for help in a GitHub issue. Analyze their question and the codebase context to provide a clear, practical solution with specific details about their code. Be helpful and informative, don't just tell them to check documentation."
                    },
                    {
                        "role": "user", 
                        "content": f"Help the user with their question:\n\n{context}"
                    }
                ],
                max_tokens=800,
                temperature=0.3
            )
            
            return response.choices[0].message.content
        else:
            # Simple fallback if no OpenAI key
            return f"""I see you need help with: "{issue['title']}"

Based on your {repo_context.get('primary_language', 'code')} repository, here are some suggestions:

1. Check the main files: {', '.join(repo_context.get('files', [])[:3])}
2. Review the issue description for specific error details
3. Look at similar issues in the repository

For more detailed AI assistance, configure your OpenAI API key."""
            
    except Exception as e:
        logger.error(f"OpenAI error: {e}")
        return f"I see your help request about '{issue['title']}'. Please check the repository documentation and similar issues for guidance."

# Helper functions (add these as well)

async def _get_repository_context(owner: str, repo: str) -> dict:
    """Get comprehensive repository context for AI analysis"""
    try:
        # Get repository info
        repo_info = await github_request("GET", f"/repos/{owner}/{repo}")
        
        # Get recent commits for activity context
        commits = await github_request("GET", f"/repos/{owner}/{repo}/commits?per_page=10")
        
        # Get repository structure (top-level files)
        try:
            contents = await github_request("GET", f"/repos/{owner}/{repo}/contents")
            files = [item["name"] for item in contents if item["type"] == "file"][:20]
        except:
            files = []
        
        # Get README if available
        readme_content = ""
        try:
            readme = await github_request("GET", f"/repos/{owner}/{repo}/readme")
            readme_content = base64.b64decode(readme["content"]).decode('utf-8')[:1000]
        except:
            pass
        
        return {
            "primary_language": repo_info.get("language"),
            "description": repo_info.get("description", ""),
            "recent_commits": len(commits),
            "files": files,
            "size": repo_info.get("size", 0),
            "stars": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "readme_snippet": readme_content[:500] if readme_content else "",
            "topics": repo_info.get("topics", [])
        }
    except Exception as e:
        logger.error(f"Error getting repository context: {e}")
        return {"error": f"Failed to get repository context: {str(e)}"}

if __name__ == "__main__":
    import os
    host = os.getenv('MCP_HOST', '0.0.0.0')  # Listen on all interfaces
    port = int(os.getenv('MCP_PORT', 8003))  # Different port for each
    mcp.run(host=host, port=port)