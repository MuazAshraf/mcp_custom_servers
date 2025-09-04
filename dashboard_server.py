#!/usr/bin/env python3
"""
Dashboard MCP Server - Token Based
Simple API integration using API key
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
DASHBOARD_BASE_URL = os.getenv("DASHBOARD_BASE_URL", "https://staging.exitmvp.com/api/v1")
DASHBOARD_API_KEY = os.getenv("DASHBOARD_API_KEY")
DASHBOARD_REFERER_URL = os.getenv("DASHBOARD_REFERER_URL", "https://dev.mojomosaic.com/")

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

async def get_prompt_id_by_name(prompt_name: str, org_name: str = None) -> str:
    """Get prompt ID by name, optionally filtered by organization"""
    try:
        # Build the endpoint with optional organization filter
        endpoint = "/prompts/"
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            endpoint = f"/prompts/?organization={org_id}"
        
        response = await make_api_request("GET", endpoint)
        prompts = response.get("results", response) if isinstance(response, dict) else response
        
        for prompt in prompts:
            if prompt.get("name") == prompt_name:
                return prompt.get("id")
        
        raise ValueError(f"Prompt '{prompt_name}' not found")
    except Exception as e:
        raise ValueError(f"Error finding prompt: {str(e)}")

async def get_tool_id_by_name(tool_name: str, org_name: str = None) -> str:
    """Get tool ID by name, optionally filtered by organization"""
    try:
        # Build the endpoint with optional organization filter
        endpoint = "/tools/"
        if org_name:
            org_id = await get_org_id_by_name(org_name)
            endpoint = f"/tools/?organization={org_id}"
        
        response = await make_api_request("GET", endpoint)
        tools = response.get("results", response) if isinstance(response, dict) else response
        
        for tool in tools:
            if tool.get("name") == tool_name:
                return tool.get("id")
        
        raise ValueError(f"Tool '{tool_name}' not found")
    except Exception as e:
        raise ValueError(f"Error finding tool: {str(e)}")


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
    """Make HTTP request to dashboard API with API key"""
    # Get API key from environment (supports both .env file and runtime updates)
    api_key = os.environ.get('DASHBOARD_API_KEY') or DASHBOARD_API_KEY
    
    # Validate API key before making request
    if not api_key:
        raise ValueError("DASHBOARD_API_KEY environment variable is required. Please set it using set_dashboard_config or in your environment.")
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Dashboard-MCP-Server",
        "Authorization": f"ApiKey {api_key}",
        "Referer": os.environ.get('DASHBOARD_REFERER_URL', 'https://staging.exitmvp.com')
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

# ===== TESTING & CONNECTION =====
@mcp.tool()
async def test_token() -> str:
    """Test if the API key is working"""
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

@mcp.tool()
async def set_dashboard_config(api_key: str = None, referer_url: str = None) -> str:
    """Set dashboard configuration (API key and referer URL)
    
    Args:
        api_key: Dashboard API key
        referer_url: Referer URL for API requests (e.g., 'https://dev.mojomosaic.com/')
    """
    try:
        config = {}
        
        if api_key:
            config['DASHBOARD_API_KEY'] = api_key
        if referer_url:
            config['DASHBOARD_REFERER_URL'] = referer_url
            
        # Update environment variables
        for key, value in config.items():
            os.environ[key] = value
            
        return json.dumps({
            "message": "Configuration updated successfully",
            "updated": config
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_dashboard_config() -> str:
    """Get current dashboard configuration"""
    try:
        config = {
            "api_key": os.environ.get('DASHBOARD_API_KEY', 'Not set'),
            "referer_url": os.environ.get('DASHBOARD_REFERER_URL', 'Not set'),
            "base_url": os.environ.get('DASHBOARD_BASE_URL', 'Not set')
        }
        return json.dumps(config, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
    
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
async def get_organization_features() -> str:
    """Get organization features settings"""
    try:
        response = await make_api_request("GET", "/organization-features/")
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
    

@mcp.tool()
async def create_organization_prompt(org_name: str, name: str, description: str, content: str, prompt_type: str = "system") -> str:
    """Create a prompt for a specific organization"""
    try:
        org_id = await get_org_id_by_name(org_name)
        data = {
            "name": name,
            "description": description,
            "content": content,
            "prompt_type": prompt_type,
            "is_global": False,
            "organization": org_id
        }
        response = await make_api_request("POST", "/prompts/", data=data)
        return json.dumps({
            "organization": org_name,
            "prompt": response,
            "message": f"Created prompt '{name}' for organization '{org_name}'"
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def create_organization_experience(org_name: str, name: str, description: str, instructions: str, 
                                       tool_names: str = "", prompt_names: str = "") -> str:
    """Create an experience for a specific organization with optional tools and prompts
    
    Args:
        org_name: Organization name (e.g. 'BrainFreeze')
        name: Experience name
        description: Experience description  
        instructions: Experience instructions
        tool_names: Optional comma-separated tool names (e.g. 'Tool1,Tool2')
        prompt_names: Optional comma-separated prompt names (e.g. 'Prompt1,Prompt2')
    """
    try:
        org_id = await get_org_id_by_name(org_name)
        
        # Create the experience first
        data = {
            "name": name,
            "description": description,
            "instructions": instructions,
            "is_global": False,
            "organization": org_id
        }
        experience = await make_api_request("POST", "/experiences/", data=data)
        exp_id = experience["id"]
        
        results = {"organization": org_name, "experience": experience, "additions": []}
        
        # Add tools if provided
        if tool_names.strip():
            for tool_name in tool_names.split(","):
                tool_name = tool_name.strip()
                if tool_name:
                    try:
                        tool_id = await get_tool_id_by_name(tool_name, org_name)
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
                        prompt_id = await get_prompt_id_by_name(prompt_name, org_name)
                        await make_api_request("POST", f"/experiences/{exp_id}/add_prompt/", {
                            "prompt_id": prompt_id, "order": i, "is_hidden": False
                        })
                        results["additions"].append(f"Added prompt '{prompt_name}'")
                    except Exception as e:
                        results["additions"].append(f"Failed to add prompt '{prompt_name}': {str(e)}")
        
        return json.dumps(results, indent=2)
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
                        tool_id = await get_tool_id_by_name(tool_name)  # No org_name = global search
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
                        prompt_id = await get_prompt_id_by_name(prompt_name)  # No org_name = global search
                        await make_api_request("POST", f"/experiences/{exp_id}/add_prompt/", {
                            "prompt_id": prompt_id, "order": i, "is_hidden": False
                        })
                        results["additions"].append(f"Added prompt '{prompt_name}'")
                    except Exception as e:
                        results["additions"].append(f"Failed to add prompt '{prompt_name}': {str(e)}")
        
        return json.dumps(results, indent=2)
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


# PRD ENDPOINTS
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
async def get_prd_types() -> str:
    """Get all PRD types"""
    try:
        response = await make_api_request("GET", "/prd/types/")
        return json.dumps(response, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

@mcp.tool()
async def get_prd_types_for_prompt(prompt_name: str) -> str:
    """Get all PRD types associated with a specific prompt by name"""
    try:
        prompt_id = await get_prd_prompt_id_by_name(prompt_name)
        response = await make_api_request("GET", f"/prd/prompts/{prompt_id}/associated_types/")
        return json.dumps({
            "prompt_name": prompt_name,
            "associated_types": response,
            "message": f"Found {len(response) if isinstance(response, list) else 0} PRD types for prompt '{prompt_name}'"
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