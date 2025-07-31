#!/usr/bin/env python3
"""
Mailgun MCP Server with Multi-Account Support for FastAPI deployment
"""

import os
import json
import base64
import logging
from typing import Dict, Any, Optional, List
import httpx
from dotenv import load_dotenv

from mcp import ClientSession, server
from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool

# Load environment variables from .env file
load_dotenv('.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("mailgun-multi-account", stateless_http=True)

# Global state for accounts
ACCOUNTS: Dict[str, Dict[str, str]] = {}
CURRENT_ACCOUNT: Optional[str] = None


def load_accounts():
    """Load Mailgun accounts from environment variables"""
    global ACCOUNTS, CURRENT_ACCOUNT
    
    # Load from MAILGUN_ACCOUNTS JSON
    accounts_json = os.getenv('MAILGUN_ACCOUNTS')
    if accounts_json:
        try:
            ACCOUNTS = json.loads(accounts_json)
            logger.info(f"Loaded {len(ACCOUNTS)} accounts from MAILGUN_ACCOUNTS")
        except json.JSONDecodeError:
            logger.error("Failed to parse MAILGUN_ACCOUNTS JSON")
    
    # Also check for individual account env vars
    for i in range(1, 10):  # Support up to 9 accounts
        key_var = f'MAILGUN_ACCOUNT_{i}_KEY'
        domain_var = f'MAILGUN_ACCOUNT_{i}_DOMAIN'
        name_var = f'MAILGUN_ACCOUNT_{i}_NAME'
        
        api_key = os.getenv(key_var)
        domain = os.getenv(domain_var)
        name = os.getenv(name_var, f'account_{i}')
        
        if api_key and domain:
            ACCOUNTS[name] = {
                'api_key': api_key,
                'domain': domain
            }
            logger.info(f"Loaded account '{name}' from environment variables")
    
    # Set first account as current if available
    if ACCOUNTS and not CURRENT_ACCOUNT:
        CURRENT_ACCOUNT = next(iter(ACCOUNTS))
        logger.info(f"Set current account to: {CURRENT_ACCOUNT}")


# Load accounts on startup
load_accounts()


async def make_mailgun_request(method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
    """Make a request to Mailgun API"""
    if not CURRENT_ACCOUNT:
        raise ValueError("No account selected")
    
    account = ACCOUNTS.get(CURRENT_ACCOUNT)
    if not account:
        raise ValueError(f"Account '{CURRENT_ACCOUNT}' not found")
    
    api_key = account['api_key']
    base_url = "https://api.mailgun.net/v3"
    
    # Create auth header
    auth_string = base64.b64encode(f"api:{api_key}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_string}"
    }
    
    url = f"{base_url}{endpoint}"
    
    async with httpx.AsyncClient() as client:
        if method == "GET":
            response = await client.get(url, headers=headers, params=params)
        elif method == "POST":
            response = await client.post(url, headers=headers, data=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        response.raise_for_status()
        return response.json()


# Account Management Tools

@mcp.tool()
async def list_accounts() -> str:
    """List all configured Mailgun accounts"""
    accounts_info = []
    for account_name, account_data in ACCOUNTS.items():
        is_current = account_name == CURRENT_ACCOUNT
        accounts_info.append({
            "name": account_name,
            "domain": account_data.get("domain"),
            "is_current": is_current
        })
    
    return json.dumps({
        "accounts": accounts_info,
        "total": len(accounts_info)
    }, indent=2)


@mcp.tool()
async def switch_account(account_name: str) -> str:
    """Switch to a different Mailgun account
    
    Args:
        account_name: Name of the account to switch to
    """
    global CURRENT_ACCOUNT
    
    if account_name not in ACCOUNTS:
        return f"Error: Account '{account_name}' not found. Available accounts: {list(ACCOUNTS.keys())}"
    
    CURRENT_ACCOUNT = account_name
    return f"Switched to account: {account_name}"


@mcp.tool()
async def get_current_account() -> str:
    """Get the currently active Mailgun account"""
    if not CURRENT_ACCOUNT:
        return "No account currently selected"
    
    account_data = ACCOUNTS.get(CURRENT_ACCOUNT, {})
    return json.dumps({
        "current_account": CURRENT_ACCOUNT,
        "domain": account_data.get("domain")
    }, indent=2)


# Email Operations

@mcp.tool()
async def send_email(
    to: str,
    subject: str,
    text: str,
    html: Optional[str] = None,
    from_email: Optional[str] = None
) -> str:
    """Send an email using the current Mailgun account
    
    Args:
        to: Recipient email address
        subject: Email subject
        text: Plain text body of the email
        html: HTML body of the email (optional)
        from_email: Sender email address (optional, uses domain default if not specified)
    """
    account = ACCOUNTS.get(CURRENT_ACCOUNT, {})
    domain = account.get('domain')
    
    if not domain:
        raise ValueError("No domain configured for current account")
    
    # Prepare email data
    email_data = {
        'to': to,
        'subject': subject,
        'text': text
    }
    
    # Add optional fields
    # if html:
    #     email_data['html'] = html
    
    if from_email:
        email_data['from'] = from_email
    else:
        # Use the domain name as the local part for the default email
        domain_name = domain.split('.')[0]  # Gets 'projectwe' from 'projectwe.com'
        email_data['from'] = f"{domain_name}@{domain}"
    
    # Send email
    result = await make_mailgun_request(
        "POST",
        f"/{domain}/messages",
        data=email_data
    )
    
    return json.dumps({
        "status": "sent",
        "account": CURRENT_ACCOUNT,
        "domain": domain,
        "message_id": result.get("id"),
        "message": result.get("message")
    }, indent=2)


# Domain & Stats Operations

@mcp.tool()
async def get_domains() -> str:
    """Get all domains for the current Mailgun account"""
    result = await make_mailgun_request("GET", "/domains")
    return json.dumps({
        "account": CURRENT_ACCOUNT,
        "domains": result.get("items", []),
        "total": result.get("total_count", 0)
    }, indent=2)


@mcp.tool()
async def get_stats(
    event: str = "delivered",
    duration: str = "7d"
) -> str:
    """Get email statistics for the current account
    
    Args:
        event: Event type (accepted, delivered, failed, opened, clicked, unsubscribed, complained, stored)
        duration: Duration (1d, 7d, 30d)
    """
    account = ACCOUNTS.get(CURRENT_ACCOUNT, {})
    domain = account.get('domain')
    
    if not domain:
        raise ValueError("No domain configured for current account")
    
    params = {
        "event": event,
        "duration": duration
    }
    
    result = await make_mailgun_request(
        "GET",
        f"/{domain}/stats/total",
        params=params
    )
    
    return json.dumps({
        "account": CURRENT_ACCOUNT,
        "domain": domain,
        "stats": result.get("stats", []),
        "resolution": result.get("resolution")
    }, indent=2)


@mcp.tool()
async def get_events(
    limit: int = 25,
    event: Optional[str] = None
) -> str:
    """Get recent events for the current account
    
    Args:
        limit: Number of events to retrieve (1-300)
        event: Filter by event type (optional)
    """
    account = ACCOUNTS.get(CURRENT_ACCOUNT, {})
    domain = account.get('domain')
    
    if not domain:
        raise ValueError("No domain configured for current account")
    
    params = {
        "limit": min(max(limit, 1), 300)  # Clamp between 1 and 300
    }
    
    if event:
        params["event"] = event
    
    result = await make_mailgun_request(
        "GET",
        f"/{domain}/events",
        params=params
    )
    
    return json.dumps({
        "account": CURRENT_ACCOUNT,
        "domain": domain,
        "events": result.get("items", []),
        "count": len(result.get("items", []))
    }, indent=2)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")