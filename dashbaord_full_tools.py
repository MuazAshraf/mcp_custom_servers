#!/usr/bin/env python3
"""
Dashboard MCP Server - Token Based
Simple API integration using hardcoded authentication token
"""

import json
import os
from pathlib import Path
import logging
from typing import Any, Dict, List, Optional
import ssl

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv('.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dashboard-mcp-server-token")

# Dashboard configuration
DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL") 
HARDCODED_TOKEN = os.getenv("HARDCODED_TOKEN")

# Create FastMCP server with stateless HTTP for FastAPI mounting
mcp = FastMCP("dashboard", stateless_http=True)

# Helper functions to get IDs by names
async def get_org_id_by_name(org_name: str) -> str:
    """Get organization ID by name"""
    try:
        orgs = await make_api_request("GET", "/organizations/")
        for org in orgs:
            if org["name"].lower() == org_name.lower() or org["slug"].lower() == org_name.lower():
                return org["id"]
        raise Exception(f"Organization '{org_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find organization '{org_name}': {str(e)}")

async def get_experience_id_by_name(experience_name: str) -> str:
    """Get experience ID by name"""
    try:
        experiences = await make_api_request("GET", "/experiences/")
        if "results" in experiences:
            for exp in experiences["results"]:
                if exp["name"].lower() == experience_name.lower():
                    return exp["id"]
        raise Exception(f"Experience '{experience_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find experience '{experience_name}': {str(e)}")

async def get_prompt_id_by_name(prompt_name: str) -> str:
    """Get prompt ID by name"""
    try:
        prompts = await make_api_request("GET", "/prompts/")
        if "results" in prompts:
            for prompt in prompts["results"]:
                if prompt["name"].lower() == prompt_name.lower():
                    return prompt["id"]
        raise Exception(f"Prompt '{prompt_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find prompt '{prompt_name}': {str(e)}")

async def get_tool_id_by_name(tool_name: str) -> str:
    """Get tool ID by name"""
    try:
        tools = await make_api_request("GET", "/tools/")
        if "results" in tools:
            for tool in tools["results"]:
                if tool["name"].lower() == tool_name.lower():
                    return tool["id"]
        raise Exception(f"Tool '{tool_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find tool '{tool_name}': {str(e)}")

async def get_conversation_id_by_title(conversation_title: str) -> str:
    """Get conversation ID by title"""
    try:
        conversations = await make_api_request("GET", "/conversations/")
        for conv in conversations:
            if conv["title"].lower() == conversation_title.lower():
                return conv["id"]
        raise Exception(f"Conversation '{conversation_title}' not found")
    except Exception as e:
        raise Exception(f"Could not find conversation '{conversation_title}': {str(e)}")
    
async def get_brain_id_by_name(brain_name: str) -> str:
    """Get brain ID by name"""
    try:
        brains = await make_api_request("GET", "/brains/")
        if "results" in brains:
            for brain in brains["results"]:
                if brain["name"].lower() == brain_name.lower():
                    return brain["id"]
        elif isinstance(brains, list):
            for brain in brains:
                if brain["name"].lower() == brain_name.lower():
                    return brain["id"]
        raise Exception(f"Brain '{brain_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find brain '{brain_name}': {str(e)}")

async def get_prd_prompt_id_by_name(prompt_name: str) -> str:
    """Get PRD prompt ID by name"""
    try:
        prompts = await make_api_request("GET", "/prd/prompts/")
        if "results" in prompts:
            for prompt in prompts["results"]:
                if prompt["name"].lower() == prompt_name.lower():
                    return prompt["id"]
        raise Exception(f"PRD Prompt '{prompt_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find PRD prompt '{prompt_name}': {str(e)}")

async def get_prd_type_id_by_name(type_name: str) -> str:
    """Get PRD type ID by name"""
    try:
        types = await make_api_request("GET", "/prd/types/")
        if "results" in types:
            for prd_type in types["results"]:
                if prd_type["name"].lower() == type_name.lower():
                    return prd_type["id"]
        raise Exception(f"PRD Type '{type_name}' not found")
    except Exception as e:
        raise Exception(f"Could not find PRD type '{type_name}': {str(e)}")

async def make_api_request(method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
    """Make HTTP request to dashboard API with hardcoded token"""
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Dashboard-MCP-Server",
        "Authorization": f"Bearer {HARDCODED_TOKEN}"
    }
    
    url = f"{DASHBOARD_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    
    # Create SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.request(method, url, headers=headers, json=data) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Dashboard API error {response.status}: {error_text}")
            
            return await response.json()

# # ===== TESTING & CONNECTION =====
@mcp.tool()
async def test_token() -> str:
    """Test if the hardcoded token is working"""
    try:
        response = await make_api_request("GET", "/organizations/")
        return json.dumps({
            "success": True,
            "message": "Token is working!",
            "organizations_count": len(response) if isinstance(response, list) else "N/A"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e),
            "message": "Token is not working. Check your .env file."
        }, indent=2)
    

# ===== ORGANIZATIONS =====
@mcp.tool()
async def list_my_organizations() -> str:
    """List all organizations with names and IDs for easy reference"""
    try:
        orgs = await make_api_request("GET", "/organizations/")
        simple_list = []
        for org in orgs:
            simple_list.append({
                "name": org["name"],
                "id": org["id"],
                "members": org["members_count"],
                "domain": org.get("domain", ""),
                "homepage": org.get("homepage_route", "/dashboard")
            })
        
        return json.dumps({
            "organizations": simple_list,
            "total": len(simple_list),
            "usage_tip": "Use organization name in other functions, like: get_org_conversations('BrainFreeze')"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_organizations() -> str:
    """Get user's organizations"""
    try:
        response = await make_api_request("GET", "/organizations/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_current_user() -> str:
    """Get current user information"""
    try:
        response = await make_api_request("GET", "/users/me/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_user_organizations() -> str:
    """Get detailed user organization memberships"""
    try:
        response = await make_api_request("GET", "/user/organizations/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_organization_features() -> str:
    """Get organization features settings"""
    try:
        response = await make_api_request("GET", "/organization-features/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_conversations(limit: int = 20) -> str:
    """Get user's conversations"""
    try:
        response = await make_api_request("GET", f"/conversations/?limit={limit}")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def create_organization(name: str, slug: str, description: str = "", website: str = "", homepage_route: str = "/dashboard") -> str:
    """Create a new organization"""
    try:
        data = {
            "name": name,
            "slug": slug,
            "description": description,
            "website": website,
            "homepage_route": homepage_route
        }
        response = await make_api_request("POST", "/organizations/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    

# ===== CONVERSATIONS =====
@mcp.tool()
async def get_org_conversations(org_name: str, limit: int = 20) -> str:
    """Get conversations for an organization by name (e.g. 'BrainFreeze')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        response = await make_api_request("GET", f"/conversations/?organization={org_id}&limit={limit}")
        return json.dumps({
            "organization": org_name,
            "conversations": response,
            "total": len(response) if isinstance(response, list) else 0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_conversation_messages_by_title(conversation_title: str) -> str:
    """Get messages from conversation by title (e.g. 'Planning Meeting')"""
    try:
        conv_id = await get_conversation_id_by_title(conversation_title)
        response = await make_api_request("GET", f"/conversations/{conv_id}/messages/")
        return json.dumps({
            "conversation": conversation_title,
            "messages": response,
            "total": len(response) if isinstance(response, list) else 0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_conversation_details_by_title(conversation_title: str) -> str:
    """Get detailed conversation info by title (e.g. 'Planning Meeting')"""
    try:
        conv_id = await get_conversation_id_by_title(conversation_title)
        response = await make_api_request("GET", f"/conversations/{conv_id}/")
        return json.dumps({
            "conversation": conversation_title,
            "details": response
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def send_message_to_conversation(conversation_title: str, message: str) -> str:
    """Send message to conversation by title (e.g. 'Planning Meeting', 'Hello AI!')"""
    try:
        conv_id = await get_conversation_id_by_title(conversation_title)
        data = {"content": message}
        response = await make_api_request("POST", f"/conversations/{conv_id}/add_message_streaming/", data=data)
        return json.dumps({
            "conversation": conversation_title,
            "message": message,
            "result": response,
            "success": f"Sent message to '{conversation_title}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

    
@mcp.tool()
async def create_conversation(title: str, org_name: str = "") -> str:
    """Create a new conversation (e.g. 'Planning Meeting', 'BrainFreeze')"""
    try:
        data = {"title": title}
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            data["organization_id"] = org_id
        response = await make_api_request("POST", "/conversations/", data=data)
        return json.dumps({
            "title": title,
            "organization": org_name or "All",
            "result": response,
            "message": f"Created conversation '{title}'" + (f" in {org_name}" if org_name else "")
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_org_conversation(org_name: str, title: str) -> str:
    """Create conversation in organization by name (e.g. 'BrainFreeze', 'Planning Meeting')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        data = {"title": title, "organization_id": org_id}
        response = await make_api_request("POST", "/conversations/", data=data)
        return json.dumps({
            "organization": org_name,
            "conversation": response,
            "message": f"Created conversation '{title}' in {org_name}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
# ===== DOCUMENTS =====
@mcp.tool()
async def search_documents(query: str) -> str:
    """Search documents"""
    try:
        data = {"query": query}
        response = await make_api_request("POST", "/search/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_org_documents(org_name: str) -> str:
    """Get documents for an organization by name (e.g. 'ProjectWE Process')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        response = await make_api_request("GET", f"/documents/?organization={org_id}")
        return json.dumps({
            "organization": org_name,
            "documents": response,
            "total": len(response) if isinstance(response, list) else 0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_document_by_name(org_name: str, document_name: str) -> str:
    """Get document details by name (e.g. 'RFN', 'report.pdf')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        docs = await make_api_request("GET", f"/documents/?organization={org_id}")
        
        for doc in docs:
            if doc["name"].lower() == document_name.lower():
                return json.dumps({
                    "organization": org_name,
                    "document_name": document_name,
                    "details": doc
                }, indent=2)
        
        return json.dumps({"error": f"Document '{document_name}' not found in '{org_name}'"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def upload_file_to_org(org_name: str, file_path: str) -> str:
    """Upload actual file to organization by name (e.g. 'RFN', '/path/to/report.pdf')"""
    try:
        import base64
        from pathlib import Path
        
        # Read the actual file
        file = Path(file_path)
        if not file.exists():
            raise Exception(f"File not found: {file_path}")
        
        # Read file content as base64 for binary files like PDF
        with open(file_path, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')
        
        org_id = await get_org_id_by_name(org_name)
        data = {
            "organization": org_id,
            "name": file.name,
            "content": file_content,
            "content_type": "base64"  # Indicate this is base64 encoded
        }
        response = await make_api_request("POST", "/documents/", data=data)
        return json.dumps({
            "organization": org_name,
            "file_name": file.name,
            "file_path": file_path,
            "file_size": f"{file.stat().st_size / 1024:.1f} KB",
            "document": response,
            "message": f"Successfully uploaded '{file.name}' to {org_name}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def upload_text_to_org(org_name: str, file_name: str, text_content: str) -> str:
    """Upload text content to organization (e.g. 'RFN', 'notes.txt', 'my notes here')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        data = {
            "organization": org_id,
            "name": file_name,
            "content": text_content
        }
        response = await make_api_request("POST", "/documents/", data=data)
        return json.dumps({
            "organization": org_name,
            "file_name": file_name,
            "document": response,
            "message": f"Uploaded text '{file_name}' to {org_name}"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def delete_document_by_name(org_name: str, document_name: str) -> str:
    """Delete document by name (e.g. 'RFN', 'old_report.pdf')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        docs = await make_api_request("GET", f"/documents/?organization={org_id}")
        
        for doc in docs:
            if doc["name"].lower() == document_name.lower():
                doc_id = doc["id"]
                response = await make_api_request("DELETE", f"/documents/{doc_id}/")
                return json.dumps({
                    "organization": org_name,
                    "document_name": document_name,
                    "result": response,
                    "message": f"Deleted '{document_name}' from '{org_name}'"
                }, indent=2)
        
        return json.dumps({"error": f"Document '{document_name}' not found in '{org_name}'"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_messages(limit: int = 20) -> str:
    """Get all messages"""
    try:
        response = await make_api_request("GET", f"/messages/?limit={limit}")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)



# ===== EXPERIENCES =====
@mcp.tool()
async def get_experiences(is_global: bool = False, org_name: str = "") -> str:
    """Get experiences (e.g. get_experiences(True) for global, or get_experiences(False, 'BrainFreeze'))"""
    try:
        params = []
        if is_global:
            params.append("is_global=true")
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            params.append(f"organization={org_id}")
        
        endpoint = "/experiences/"
        if params:
            endpoint += "?" + "&".join(params)
            
        response = await make_api_request("GET", endpoint)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_org_experiences(org_name: str) -> str:
    """Get experiences for an organization by name (e.g. 'RFN')"""
    try:
        org_id = await get_org_id_by_name(org_name)
        response = await make_api_request("GET", f"/experiences/?organization={org_id}")
        return json.dumps({
            "organization": org_name,
            "experiences": response,
            "total": len(response) if isinstance(response, list) else 0
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_experience_by_name(experience_name: str) -> str:
    """Get experience details by name (e.g. 'Document Analysis Assistant')"""
    try:
        exp_id = await get_experience_id_by_name(experience_name)
        response = await make_api_request("GET", f"/experiences/{exp_id}/")
        return json.dumps({
            "experience_name": experience_name,
            "details": response
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_global_experience(name: str, description: str, instructions: str, 
                                 tool_names: str = "", prompt_names: str = "") -> str:
    """Create a global experience with optional tools and prompts
    
    Args:
        name: Experience name
        description: Experience description  
        instructions: Experience instructions
        tool_names: Optional comma-separated tool names (e.g. 'Tool1,Tool2')
        prompt_names: Optional comma-separated prompt names (e.g. 'Prompt1,Prompt2')
    """
    try:
        # Create the experience first
        data = {
            "name": name,
            "description": description,
            "instructions": instructions,
            "is_global": True
        }
        experience = await make_api_request("POST", "/experiences/create_global/", data=data)
        exp_id = experience["id"]
        
        results = {"experience": experience, "additions": []}
        
        # Add tools if provided
        if tool_names.strip():
            for tool_name in tool_names.split(","):
                tool_name = tool_name.strip()
                if tool_name:
                    try:
                        tool_id = await get_tool_id_by_name(tool_name)
                        await make_api_request("POST", f"/experiences/{exp_id}/add_tool/", {"tool_id": tool_id})
                        results["additions"].append(f"Added tool '{tool_name}'")
                    except Exception as e:
                        results["additions"].append(f"Failed to add tool '{tool_name}': {str(e)}")
        
        # Add prompts if provided
        if prompt_names.strip():
            for i, prompt_name in enumerate(prompt_names.split(","), 1):
                prompt_name = prompt_name.strip()
                if prompt_name:
                    try:
                        prompt_id = await get_prompt_id_by_name(prompt_name)
                        await make_api_request("POST", f"/experiences/{exp_id}/add_prompt/", {
                            "prompt_id": prompt_id, "order": i, "is_hidden": False
                        })
                        results["additions"].append(f"Added prompt '{prompt_name}'")
                    except Exception as e:
                        results["additions"].append(f"Failed to add prompt '{prompt_name}': {str(e)}")
        
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def update_experience_by_name(experience_name: str, description: str = "", instructions: str = "") -> str:
    """Update an experience by name"""
    try:
        exp_id = await get_experience_id_by_name(experience_name)
        data = {}
        if description:
            data["description"] = description
        if instructions:
            data["instructions"] = instructions
        response = await make_api_request("PATCH", f"/experiences/{exp_id}/", data=data)
        return json.dumps({
            "experience_name": experience_name,
            "updated": response,
            "message": f"Updated experience '{experience_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

# ===== PROMPTS =====
@mcp.tool()
async def get_prompts(is_global: bool = False, org_name: str = "") -> str:
    """Get prompts (e.g. get_prompts(True) for global, or get_prompts(False, 'RFN'))"""
    try:
        params = []
        if is_global:
            params.append("is_global=true")
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            params.append(f"organization={org_id}")
        
        endpoint = "/prompts/"
        if params:
            endpoint += "?" + "&".join(params)
            
        response = await make_api_request("GET", endpoint)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_prompt(name: str, description: str, content: str, prompt_type: str = "system", is_global: bool = False) -> str:
    """Create a new prompt"""
    try:
        data = {
            "name": name,
            "description": description,
            "content": content,
            "prompt_type": prompt_type,
            "is_global": is_global
        }
        response = await make_api_request("POST", "/prompts/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_global_prompt(name: str, description: str, content: str, prompt_type: str = "system") -> str:
    """Create a global prompt (superuser only)"""
    try:
        data = {
            "name": name,
            "description": description,
            "content": content,
            "prompt_type": prompt_type,
            "is_global": True
        }
        response = await make_api_request("POST", "/prompts/create_global/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    

# ===== TOOLS =====
@mcp.tool()
async def get_tools(is_global: bool = False, org_name: str = "") -> str:
    """Get tools (e.g. get_tools(True) for global, or get_tools(False, 'BrainFreeze'))"""
    try:
        params = []
        if is_global:
            params.append("is_global=true")
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            params.append(f"organization={org_id}")
        
        endpoint = "/tools/"
        if params:
            endpoint += "?" + "&".join(params)
            
        response = await make_api_request("GET", endpoint)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_tool(name: str, description: str, function_code: str, schema: Dict, is_global: bool = False) -> str:
    """Create a new tool"""
    try:
        data = {
            "name": name,
            "description": description,
            "function_code": function_code,
            "schema": schema,
            "is_global": is_global
        }
        response = await make_api_request("POST", "/tools/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def test_tool_by_name(tool_name: str, test_input: Dict) -> str:
    """Test a tool by name (e.g. 'Document Summarizer', {'content': 'test'})"""
    try:
        tool_id = await get_tool_id_by_name(tool_name)
        response = await make_api_request("POST", f"/tools/{tool_id}/test/", data=test_input)
        return json.dumps({
            "tool_name": tool_name,
            "test_input": test_input,
            "result": response
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def remove_prompt_from_experience_by_name(experience_name: str, prompt_name: str) -> str:
    """Remove prompt from experience using names"""
    try:
        exp_id = await get_experience_id_by_name(experience_name)
        prompt_id = await get_prompt_id_by_name(prompt_name)
        data = {"prompt_id": prompt_id}
        response = await make_api_request("DELETE", f"/experiences/{exp_id}/remove_prompt/", data=data)
        return json.dumps({
            "experience": experience_name,
            "prompt": prompt_name,
            "result": response,
            "message": f"Removed prompt '{prompt_name}' from experience '{experience_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def remove_tool_from_experience_by_name(experience_name: str, tool_name: str) -> str:
    """Remove tool from experience using names"""
    try:
        exp_id = await get_experience_id_by_name(experience_name)
        tool_id = await get_tool_id_by_name(tool_name)
        data = {"tool_id": tool_id}
        response = await make_api_request("DELETE", f"/experiences/{exp_id}/remove_tool/", data=data)
        return json.dumps({
            "experience": experience_name,
            "tool": tool_name,
            "result": response,
            "message": f"Removed tool '{tool_name}' from experience '{experience_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ===== AI MODELS =====
@mcp.tool()
async def get_ai_models() -> str:
    """Get AI models (superuser only)"""
    try:
        response = await make_api_request("GET", "/ai-models/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_ai_model(name: str, provider: str, model_id: str, description: str, max_tokens: int, cost_per_1k_tokens: str, is_active: bool = True) -> str:
    """Create a new AI model (superuser only)"""
    try:
        data = {
            "name": name,
            "provider": provider,
            "model_id": model_id,
            "description": description,
            "is_active": is_active,
            "max_tokens": max_tokens,
            "cost_per_1k_tokens": cost_per_1k_tokens
        }
        response = await make_api_request("POST", "/ai-models/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_default_model() -> str:
    """Get the default AI model"""
    try:
        response = await make_api_request("GET", "/ai-models/default/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def fetch_provider_models(provider: str) -> str:
    """Get available models from a provider"""
    try:
        data = {"provider": provider}
        response = await make_api_request("POST", "/ai-models/fetch_provider_models/", data=data)
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


# ===== PRD =====
@mcp.tool()
async def get_prd_types() -> str:
    """Get all PRD types"""
    try:
        response = await make_api_request("GET", "/prd/types/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
@mcp.tool()
async def get_prd_prompts(tag: str = "") -> str:
    """Get PRD prompts by tag. Valid tags: 'ceo', 'prd', 'experience'"""
    try:
        valid_tags = ["ceo", "prd", "experience"]
        if tag and tag not in valid_tags:
            return json.dumps({
                "error": f"Invalid tag '{tag}'. Use one of: {valid_tags}"
            }, indent=2)
        
        if tag:
            response = await make_api_request("GET", f"/prd/prompts/search_by_tag/?tag={tag}")
        else:
            response = await make_api_request("GET", "/prd/prompts/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_prd_prompt(name: str, description: str, content: str, tag: str = "ceo") -> str:
    """Create PRD prompt. Tags: 'ceo' (CEO analysis), 'prd' (PRD generation), 'experience' (AI experience generation)"""
    try:
        valid_tags = ["ceo", "prd", "experience"]
        if tag not in valid_tags:
            return json.dumps({
                "error": f"Invalid tag '{tag}'. Use one of: {valid_tags}"
            }, indent=2)
            
        data = {
            "name": name,
            "description": description,
            "content": content,
            "tag": [tag]
        }
        response = await make_api_request("POST", "/prd/prompts/", data=data)
        return json.dumps({
            "created": response,
            "message": f"Created PRD prompt '{name}' with tag '{tag}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_prd_type(name: str, description: str, prompt_name: str) -> str:
    """Create PRD type linked to prompt by name (e.g. 'Insurance PRD', 'Insurance PRD template', 'Insurance CEO Analysis')"""
    try:
        prompt_id = await get_prd_prompt_id_by_name(prompt_name)
        data = {
            "name": name,
            "description": description,
            "prompt": prompt_id
        }
        response = await make_api_request("POST", "/prd/types/", data=data)
        return json.dumps({
            "prd_type": name,
            "linked_prompt": prompt_name,
            "result": response,
            "message": f"Created PRD type '{name}' linked to prompt '{prompt_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def assign_prompt_to_prd_type(type_name: str, prompt_name: str) -> str:
    """Assign prompt to PRD type using names (e.g. 'Technical PRD', 'Technical PRD Generator Prompt')"""
    try:
        type_id = await get_prd_type_id_by_name(type_name)
        prompt_id = await get_prd_prompt_id_by_name(prompt_name)
        data = {"prompt_id": prompt_id}
        response = await make_api_request("POST", f"/prd/types/{type_id}/assign_prompt/", data=data)
        return json.dumps({
            "prd_type": type_name,
            "prompt": prompt_name,
            "result": response,
            "message": f"Assigned prompt '{prompt_name}' to PRD type '{type_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def update_prd_prompt_by_name(prompt_name: str, content: str = "", tag: str = "") -> str:
    """Update PRD prompt by name. Valid tags: 'ceo', 'prd', 'experience'"""
    try:
        valid_tags = ["ceo", "prd", "experience"]
        if tag and tag not in valid_tags:
            return json.dumps({
                "error": f"Invalid tag '{tag}'. Use one of: {valid_tags}"
            }, indent=2)
            
        prompt_id = await get_prd_prompt_id_by_name(prompt_name)
        data = {}
        if content:
            data["content"] = content
        if tag:
            data["tag"] = [tag]
        response = await make_api_request("PATCH", f"/prd/prompts/{prompt_id}/", data=data)
        return json.dumps({
            "prompt_name": prompt_name,
            "updated": response,
            "message": f"Updated PRD prompt '{prompt_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def delete_prd_prompt_by_name(prompt_name: str) -> str:
    """Delete PRD prompt by name (e.g. 'Old Insurance Prompt')"""
    try:
        prompt_id = await get_prd_prompt_id_by_name(prompt_name)
        response = await make_api_request("DELETE", f"/prd/prompts/{prompt_id}/")
        return json.dumps({
            "prompt_name": prompt_name,
            "result": response,
            "message": f"Deleted PRD prompt '{prompt_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


@mcp.tool()
async def remove_prompt_from_prd_type(type_name: str) -> str:
    """Remove prompt from PRD type by name (e.g. 'Technical PRD')"""
    try:
        type_id = await get_prd_type_id_by_name(type_name)
        response = await make_api_request("POST", f"/prd/types/{type_id}/remove_prompt/")
        return json.dumps({
            "prd_type": type_name,
            "result": response,
            "message": f"Removed prompt from PRD type '{type_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")