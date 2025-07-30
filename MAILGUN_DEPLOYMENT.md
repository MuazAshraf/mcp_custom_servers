# Mailgun Multi-Account Deployment Guide

## 1. Environment Variables on Digital Ocean

Add these to your server's environment:

```bash
# Option 1: All accounts in one JSON
export MAILGUN_ACCOUNTS='{"company1": {"api_key": "key-xxx", "domain": "mg.company1.com"}, "company2": {"api_key": "key-yyy", "domain": "mg.company2.com"}, "company3": {"api_key": "key-zzz", "domain": "mg.company3.com"}}'

# Option 2: Individual variables
export MAILGUN_ACCOUNT_1_NAME="company1"
export MAILGUN_ACCOUNT_1_KEY="key-xxx"
export MAILGUN_ACCOUNT_1_DOMAIN="mg.company1.com"

export MAILGUN_ACCOUNT_2_NAME="company2"
export MAILGUN_ACCOUNT_2_KEY="key-yyy"
export MAILGUN_ACCOUNT_2_DOMAIN="mg.company2.com"

export MAILGUN_ACCOUNT_3_NAME="company3"
export MAILGUN_ACCOUNT_3_KEY="key-zzz"
export MAILGUN_ACCOUNT_3_DOMAIN="mg.company3.com"
```

## 2. Claude Desktop Configuration

```json
{
  "mcpServers": {
    "mailgun": {
      "url": "http://198.199.82.44:8000/mailgun/mcp/"
    }
  }
}
```

## 3. Usage Examples

```
You: Show me all mailgun accounts
Claude: [lists company1, company2, company3]

You: Switch to company2
Claude: Switched to account: company2

You: Send test email to test@example.com
Claude: [sends from company2's domain]

You: Check email stats for company1
Claude: [switches to company1 and shows stats]
```

## Available Commands:
- `list_accounts` - See all your accounts
- `switch_account` - Change active account
- `get_current_account` - Check which account is active
- `send_email` - Send emails
- `get_stats` - View delivery statistics
- `get_events` - Check recent email events
- `get_domains` - List domains