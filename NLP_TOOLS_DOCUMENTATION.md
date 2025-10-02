# Natural Language Processing Tools Documentation

## How to Use the Dashboard MCP Server Tools

This guide shows you how to use the Dashboard MCP server tools in natural language - just like talking to Claude! You don't need to know technical details, just tell the system what you want to create.

## What You Can Create

### 1. AI Experiences
AI experiences are like specialized AI assistants that can help with specific tasks.

### 2. Prompts  
Prompts are templates that guide how the AI responds to users.

### 3. Organizations
Organizations help you organize your AI experiences and prompts.

## How to Create Things (Natural Language Examples)

### Creating a Global AI Experience

**What you say to Claude:**
"I want to create a global experience. The name is 'Customer Support Assistant', the description is 'Handles customer inquiries and provides support', the instructions are 'You are a helpful customer support assistant. Respond to customer inquiries with empathy, accuracy, and helpfulness. If you cannot resolve an issue, escalate it appropriately. Always maintain a professional and friendly tone.', and I don't want to add any tools or prompts right now."

**What Claude does:**
- Creates a global AI experience called "Customer Support Assistant"
- Sets up the description and instructions
- Makes it available for everyone to use

### Creating a Global Prompt

**What you say to Claude:**
"I want to create a global prompt. The name is 'Support Response Template', the description is 'Template for customer support responses', the content is 'Thank you for contacting us. I understand your concern about [ISSUE]. Let me help you with that. [SOLUTION]. If you need further assistance, please don't hesitate to ask.', and the prompt type is 'human'."

**What Claude does:**
- Creates a global prompt template
- Sets up the content that will guide AI responses
- Makes it available for all experiences to use

### Creating an Organization

**What you say to Claude:**
"I want to create an organization. The name is 'My Company', the slug is 'my-company', the description is 'Our company AI tools', the website is 'https://mycompany.com', and the homepage route is '/dashboard'."

**What Claude does:**
- Creates a new organization called "My Company"
- Sets up all the details you specified
- Gives you a place to organize your AI experiences

### Creating an Organization-Specific Experience

**What you say to Claude:**
"I want to create an experience for the organization 'My Company'. The name is 'Sales Coach', the description is 'Helps sales team with customer interactions', the instructions are 'You are a sales coach. Help sales representatives improve their customer interactions, provide guidance on objection handling, and suggest follow-up strategies.', and I want to add the tool 'MojoAlgo' and the prompt 'Sales Response Template'."

**What Claude does:**
- Creates an experience specifically for your organization
- Adds the tools and prompts you specified
- Makes it available only to your organization

### Creating an Organization-Specific Prompt

**What you say to Claude:**
"I want to create a prompt for the organization 'My Company'. The name is 'Sales Follow-up', the description is 'Template for sales follow-up emails', the content is 'Hi [CUSTOMER_NAME], Thank you for your interest in our product. I wanted to follow up on our conversation about [TOPIC]. Here are the next steps: [NEXT_STEPS]. Please let me know if you have any questions.', and the prompt type is 'human'."

**What Claude does:**
- Creates a prompt specific to your organization
- Sets up the email template content
- Makes it available for your organization's experiences

### Updating an Existing Experience

**What you say to Claude:**
"I want to update the experience 'Customer Support Assistant'. I want to change the name to 'Advanced Customer Support Assistant', update the description to 'Enhanced customer support with AI-powered insights', and add the prompt 'Support Response Template'."

**What Claude does:**
- Updates the existing experience with your changes
- Adds the new prompt you specified
- Keeps all other settings the same

### Updating an Existing Prompt

**What you say to Claude:**
"I want to update the prompt 'Support Response Template'. I want to change the content to 'Hello! Thank you for reaching out to us. I understand you're having an issue with [ISSUE]. Let me help you resolve this. Here's what I can do: [SOLUTION]. Is there anything else I can help you with today?' and add the tag 'customer-support'."

**What Claude does:**
- Updates the prompt content with your new text
- Adds the tag for better organization
- Keeps the name and other settings the same


## Common Use Cases (Natural Language Examples)

### 1. Sentiment Analysis Tool

**What you say to Claude:**
"I want to create a global experience for sentiment analysis. The name is 'Sentiment Analysis Tool', the description is 'Analyzes text sentiment and emotional tone', the instructions are 'You are an expert sentiment analysis tool. Analyze the provided text for emotional tone, sentiment polarity, and key emotional indicators. Provide detailed analysis with confidence scores.', and I don't need any tools or prompts right now."

### 2. Content Generator

**What you say to Claude:**
"I want to create a global experience for content generation. The name is 'Content Generator', the description is 'Generates high-quality content from structured data', the instructions are 'You are a professional content generator. Create engaging, accurate, and well-structured content based on the provided information. Ensure the content is appropriate for the target audience and maintains a consistent tone.', and I don't need any tools or prompts right now."

### 3. Translation Assistant

**What you say to Claude:**
"I want to create a global experience for translation. The name is 'Translation Assistant', the description is 'Professional translation and localization services', the instructions are 'You are a professional translator with expertise in multiple languages. Provide accurate, culturally appropriate translations that maintain the original meaning and tone. Consider cultural nuances and context.', and I don't need any tools or prompts right now."

### 4. Knowledge Assistant

**What you say to Claude:**
"I want to create a global experience for Q&A. The name is 'Knowledge Assistant', the description is 'Intelligent question answering system', the instructions are 'You are a knowledgeable assistant that provides accurate, helpful answers to user questions. Use the available knowledge base to provide comprehensive, well-sourced responses. If you don't know something, say so clearly.', and I don't need any tools or prompts right now."

### 5. Text Classifier

**What you say to Claude:**
"I want to create a global experience for text classification. The name is 'Text Classifier', the description is 'Automatically categorizes and tags text content', the instructions are 'You are an expert text classifier. Analyze the provided text and assign appropriate categories, tags, and classifications. Provide confidence scores for each classification and explain your reasoning.', and I don't need any tools or prompts right now."

## Getting Information (Natural Language Examples)

### Listing Your Experiences

**What you say to Claude:**
"Show me all my global experiences."

**What you say to Claude:**
"Show me all experiences for the organization 'My Company'."

### Listing Your Prompts

**What you say to Claude:**
"Show me all my global prompts."

**What you say to Claude:**
"Show me all prompts for the organization 'My Company'."

### Getting Specific Details

**What you say to Claude:**
"Show me details about the experience 'Customer Support Assistant'."

**What you say to Claude:**
"Show me details about the prompt 'Support Response Template'."

### Listing Your Organizations

**What you say to Claude:**
"Show me all my organizations."

## What You Need to Know

### Required Information for Creating Experiences:
- **Name**: What you want to call it
- **Description**: What it does in simple terms
- **Instructions**: How you want the AI to behave
- **Tools** (optional): Any tools you want to add
- **Prompts** (optional): Any prompts you want to add

### Required Information for Creating Prompts:
- **Name**: What you want to call it
- **Description**: What it's for
- **Content**: The actual text template
- **Prompt Type**: Either "system" or "human"

### Required Information for Creating Organizations:
- **Name**: Your organization name
- **Slug**: A short version for URLs (like "my-company")
- **Description**: What your organization does
- **Website** (optional): Your website URL
- **Homepage Route** (optional): Where users start (like "/dashboard")

## Tips for Success

1. **Be Clear**: Describe exactly what you want the AI to do
2. **Be Specific**: The more details you give, the better the results
3. **Test First**: Create simple versions first, then add complexity
4. **Use Examples**: Include examples in your instructions when possible
5. **Keep It Simple**: Start with basic functionality, then add features

## Need Help?

Just ask Claude! You can say things like:
- "I want to create a [type] for [purpose]"
- "Show me my [experiences/prompts/organizations]"
- "Update my [experience/prompt] to [changes]"
- "Help me understand what [tool] does"

Claude will guide you through the process and make sure you have everything you need!
