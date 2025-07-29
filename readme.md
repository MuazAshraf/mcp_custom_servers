# MCP Custom Servers Hub

A collection of Model Context Protocol (MCP) servers for various integrations.

## Setup Instructions

1. Create Virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On Mac/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with the following variables:
   ```
   # Fireflies API
   FIREFLIES_API_KEY=your_fireflies_api_key
   
   # GitHub API
   GITHUB_TOKEN=your_github_token
   OPENAI_API_KEY=your_openai_api_key
   
   # Vimeo API
   ACCESS_TOKEN=your_vimeo_access_token
   AUTHORIZATION_TOKEN=your_vimeo_authorization_token
   ```

5. The `.gitignore` file should already include `.env`, `venv`, `__pycache__/`

## Running the Servers

### Individual MCP Server (Development)
```bash
mcp dev filename.py
```
Example:
- `mcp dev github_server.py`
- `mcp dev fireflies_server.py`
- `mcp dev prd_server.py`
- `mcp dev vimeo_server.py`

### All Servers Together (Production)
```bash
python main.py
```
This will run all MCP servers on a single FastAPI instance at `http://localhost:8000`

## Available MCP Servers

### 1. Fireflies Server (`/fireflies`)
- Get transcripts
- Search meetings
- Upload audio for transcription
- Manage team users
- Analytics

### 2. GitHub Server (`/github`)
- Create/manage repositories
- Issues and pull requests
- Code search
- File uploads
- Auto-respond to help requests

### 3. PRD Generator Server (`/prd`)
- Generate PRDs from Fireflies transcripts
- Fetch latest transcripts

### 4. Vimeo Server (`/vimeo`)
#### Video Upload Tools
- `upload_video_tus` - Upload large video files using TUS protocol
- `upload_video_from_url` - Upload videos from URL

#### Video Management Tools
- `get_my_videos` - List all your videos
- `get_video_details` - Get detailed video information
- `update_video` - Update video metadata (title, description, privacy)
- `delete_video` - Delete a video

#### Folder Management Tools
- `create_folder` - Create folders for organization
- `get_folders` - List all folders
- `add_video_to_folder` - Add video to folder
- `remove_video_from_folder` - Remove video from folder
- `get_folder_videos` - List videos in a folder

## API Endpoints

When running via `main.py`, the servers are available at:
- Health check: `http://localhost:8000/health`
- Fireflies: `http://localhost:8000/fireflies`
- GitHub: `http://localhost:8000/github`
- PRD: `http://localhost:8000/prd`
- Vimeo: `http://localhost:8000/vimeo`
