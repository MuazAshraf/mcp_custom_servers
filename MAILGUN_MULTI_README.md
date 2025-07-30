# Mailgun Multi-Account MCP Server

This custom MCP server extends the standard Mailgun functionality to support multiple Mailgun accounts/API keys. You can switch between accounts dynamically during your session.

## Features

- **Multiple Account Support**: Configure multiple Mailgun accounts with different API keys and domains
- **Account Switching**: Switch between accounts on the fly without restarting the server
- **All Core Mailgun Features**: Send emails, get statistics, view events, manage domains
- **Account Management Tools**: List accounts, switch accounts, view current account

## Configuration

You have two options for configuring multiple accounts:

### Option 1: JSON Format (Recommended)

Set the `MAILGUN_ACCOUNTS` environment variable with a JSON object:

```json
{
    "mcpServers": {
        "mailgun-multi": {
            "command": "python",
            "args": ["path/to/mailgun_multi_server.py"],
            "env": {
                "MAILGUN_ACCOUNTS": "{\"production\": {\"api_key\": \"key1\", \"domain\": \"domain1\"}, \"staging\": {\"api_key\": \"key2\", \"domain\": \"domain2\"}}"
            }
        }
    }
}
```

### Option 2: Individual Environment Variables

Set individual environment variables for each account:

```json
{
    "mcpServers": {
        "mailgun-multi": {
            "command": "python",
            "args": ["path/to/mailgun_multi_server.py"],
            "env": {
                "MAILGUN_ACCOUNT_1_NAME": "production",
                "MAILGUN_ACCOUNT_1_KEY": "your-api-key",
                "MAILGUN_ACCOUNT_1_DOMAIN": "mg.yourdomain.com",
                
                "MAILGUN_ACCOUNT_2_NAME": "staging",
                "MAILGUN_ACCOUNT_2_KEY": "staging-api-key",
                "MAILGUN_ACCOUNT_2_DOMAIN": "mg-staging.yourdomain.com"
            }
        }
    }
}
```

## Available Tools

### Account Management

- **list_accounts**: List all configured Mailgun accounts
- **switch_account**: Switch to a different Mailgun account
- **get_current_account**: Get the currently active account

### Email Operations

- **send_email**: Send an email using the current account
  - Required: `to`, `subject`, `text`
  - Optional: `html`, `from`

### Domain & Stats

- **get_domains**: Get all domains for the current account
- **get_stats**: Get email statistics
  - Optional: `event` (accepted, delivered, failed, etc.), `duration` (1d, 7d, 30d)
- **get_events**: Get recent events
  - Optional: `limit` (1-300), `event` filter

## Usage Examples

### List all accounts
```
Use the list_accounts tool
```

### Switch to a different account
```
Use the switch_account tool with account_name: "production"
```

### Send an email
```
Use the send_email tool with:
- to: "recipient@example.com"
- subject: "Test Email"
- text: "This is a test email"
- html: "<h1>This is a test email</h1>" (optional)
```

### Get statistics
```
Use the get_stats tool with:
- event: "delivered"
- duration: "7d"
```

## Notes

- The first configured account is automatically set as the current account
- All API operations use the currently selected account
- You can configure up to 9 accounts using individual environment variables
- The server maintains the account state throughout the session