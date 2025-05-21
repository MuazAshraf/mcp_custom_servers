# PRD Generator

A service that converts meeting transcripts from Fireflies.ai into structured Product Requirements Documents (PRDs) using OpenAI.

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Fireflies API key

## Quick Start (Using run.py - Cross-platform)

The easiest way to run this application on any platform (Windows):

```bash
# Setup the environment (first time only)
python scripts/run.py setup

# Edit the .env file with your actual API keys
# (Use any text editor)

# Start the application
python scripts/run.py server

# Start in background (Mac/Linux only)
python scripts/run.py server --daemon

# Stop the background server (Mac/Linux only)
python scripts/run.py stop
```

```windows
# Setup the environment (first time only)
.\run_windows.bat setup

# Start the application
.\run_windows.bat server


This script handles setting up the virtual environment, installing dependencies, and running the application for you automatically.

## Manual Setup (Alternative)

1. Create a virtual environment:
   ```
   python -m venv venv
   ```
2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Mac/Linux: `source venv/bin/activate`
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key
   FIREFLIES_API_KEY=your_fireflies_api_key
   ```
5. Run the application:
   ```
   mcp dev prd_server.py
   ```

## Features

- Connect to Fireflies.ai and fetch the latest meeting transcript
- Generate structured PRDs using OpenAI's GPT-4o-mini model
- Simple REST API for accessing functionality

## API Endpoints

- `/fetch_latest_transcript` - Fetch the latest transcript from Fireflies
- `/generate_prd` - Generate a PRD from the fetched transcript