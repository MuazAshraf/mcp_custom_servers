from mcp.server.fastmcp import FastMCP
import requests, os, time
from dotenv import load_dotenv
from typing import Dict, Optional, List
import logging

load_dotenv('.env')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vimeo-mcp-server")

# Initialize the MCP server with stateless HTTP for FastAPI mounting
mcp = FastMCP("VimeoServer", stateless_http=True)

# Vimeo configuration
# Use VIMEO_API_KEY for clarity - this should be your Vimeo personal access token
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")


VIMEO_API_BASE = "https://api.vimeo.com"

# Headers for Vimeo API requests
def get_headers():
    return {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.vimeo.*+json;version=3.4"
    }

# Helper function to make requests to Vimeo API
def vimeo_request(method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
    """Make a request to the Vimeo API"""
    try:
        url = f"{VIMEO_API_BASE}/{endpoint.lstrip('/')}"
        
        response = requests.request(
            method=method,
            url=url,
            headers=get_headers(),
            json=data,
            params=params
        )
        
        if response.status_code >= 400:
            return {"error": f"Vimeo API error {response.status_code}: {response.text}"}
        
        return response.json() if response.text else {"success": True}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# ===== VIDEO UPLOAD TOOLS =====

@mcp.tool()
def upload_video_tus(file_path: str, title: str = "", description: str = "", privacy: str = "unlisted") -> Dict:
    """
    Upload a video to Vimeo using TUS protocol (for large files)
    
    Args:
        file_path: Absolute path to the video file
        title: Video title
        description: Video description
        privacy: Privacy setting (public, unlisted, private, password)
        
    Returns:
        Upload result with video URI and upload status
    """
    if not os.path.exists(file_path):
        return {"error": f"File not found: {file_path}"}
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return {"error": f"File is empty: {file_path}"}
    
    # Step 1: Create upload session
    body = {
        "upload": {
            "approach": "tus",
            "size": str(file_size)
        },
        "name": title or os.path.basename(file_path),
        "description": description,
        "privacy": {
            "view": privacy
        }
    }
    
    create_response = vimeo_request("POST", "/me/videos", data=body)
    if "error" in create_response:
        return create_response
    
    upload_link = create_response.get("upload", {}).get("upload_link")
    video_uri = create_response.get("uri")
    
    if not upload_link or not video_uri:
        return {"error": "Failed to get upload link or video URI"}
    
    # Step 2: Upload the file in chunks
    chunk_size = 1048576  # 1MB chunks
    offset = 0
    
    try:
        with open(file_path, 'rb') as f:
            while offset < file_size:
                f.seek(offset)
                data = f.read(chunk_size)
                
                patch_headers = {
                    "Authorization": f"Bearer {ACCESS_TOKEN}",
                    "Tus-Resumable": "1.0.0",
                    "Upload-Offset": str(offset),
                    "Content-Type": "application/offset+octet-stream"
                }
                
                response = requests.patch(upload_link, headers=patch_headers, data=data)
                
                if response.status_code == 204:
                    offset = int(response.headers.get("Upload-Offset", offset))
                    logger.info(f"Uploaded {offset}/{file_size} bytes ({offset*100//file_size}%)")
                else:
                    return {"error": f"Upload failed at offset {offset}: {response.status_code}"}
        
        # Verify upload completion
        head_headers = {
            "Tus-Resumable": "1.0.0",
            "Authorization": f"Bearer {ACCESS_TOKEN}"
        }
        
        response = requests.head(upload_link, headers=head_headers)
        if response.status_code == 200:
            upload_offset = int(response.headers.get("Upload-Offset", 0))
            upload_length = int(response.headers.get("Upload-Length", 0))
            
            if upload_offset == upload_length:
                return {
                    "success": True,
                    "video_uri": video_uri,
                    "video_id": video_uri.split("/")[-1],
                    "upload_status": "complete",
                    "title": title or os.path.basename(file_path),
                    "message": "Video uploaded successfully. Processing may take a few minutes."
                }
    
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}
    
    return {"error": "Upload verification failed"}

@mcp.tool()
def upload_video_from_url(url: str, title: str, description: str = "", privacy: str = "unlisted") -> Dict:
    """
    Upload a video to Vimeo from a URL (pull upload)
    
    Args:
        url: HTTPS URL of the video file
        title: Video title
        description: Video description
        privacy: Privacy setting (public, unlisted, private, password)
        
    Returns:
        Upload result with video URI
    """
    body = {
        "upload": {
            "approach": "pull",
            "link": url
        },
        "name": title,
        "description": description,
        "privacy": {
            "view": privacy
        }
    }
    
    response = vimeo_request("POST", "/me/videos", data=body)
    
    if "error" not in response and "uri" in response:
        response["video_id"] = response["uri"].split("/")[-1]
        response["message"] = "Video upload initiated. Processing may take some time."
    
    return response

# ===== VIDEO MANAGEMENT TOOLS =====

@mcp.tool()
def get_my_videos(page: int = 1, per_page: int = 25, sort: str = "date", direction: str = "desc") -> Dict:
    """
    Get authenticated user's videos
    
    Args:
        page: Page number
        per_page: Number of items per page (max 100)
        sort: Sort field (date, alphabetical, plays, likes, comments, duration)
        direction: Sort direction (asc, desc)
        
    Returns:
        List of user's videos with metadata
    """
    params = {
        "page": page,
        "per_page": min(per_page, 100),
        "sort": sort,
        "direction": direction
    }
    
    response = vimeo_request("GET", "/me/videos", params=params)
    
    if "error" not in response and "data" in response:
        # Simplify the response with key information
        videos = []
        for video in response.get("data", []):
            videos.append({
                "video_id": video.get("uri", "").split("/")[-1],
                "title": video.get("name"),
                "description": video.get("description"),
                "duration": video.get("duration"),
                "created_time": video.get("created_time"),
                "privacy": video.get("privacy", {}).get("view"),
                "link": video.get("link"),
                "plays": video.get("stats", {}).get("plays", 0),
                "status": video.get("transcode", {}).get("status", "unknown")
            })
        
        return {
            "total": response.get("total", 0),
            "page": response.get("page", 1),
            "per_page": response.get("per_page", 25),
            "videos": videos
        }
    
    return response

@mcp.tool()
def get_video_details(video_id: str) -> Dict:
    """
    Get detailed information about a specific video
    
    Args:
        video_id: Video ID or URI (e.g., "123456789" or "/videos/123456789")
        
    Returns:
        Complete video metadata including transcode status
    """
    # Clean the video_id to ensure it's just the numeric ID
    video_id = video_id.strip("/").split("/")[-1]
    response = vimeo_request("GET", f"/videos/{video_id}")
    
    if "error" not in response:
        # Extract key information
        return {
            "video_id": video_id,
            "title": response.get("name"),
            "description": response.get("description"),
            "duration": response.get("duration"),
            "created_time": response.get("created_time"),
            "modified_time": response.get("modified_time"),
            "privacy": response.get("privacy", {}).get("view"),
            "link": response.get("link"),
            "embed_html": response.get("embed", {}).get("html"),
            "plays": response.get("stats", {}).get("plays", 0),
            "transcode_status": response.get("transcode", {}).get("status"),
            "upload_status": response.get("upload", {}).get("status"),
            "download": response.get("download"),
            "pictures": response.get("pictures", {}).get("sizes", [])
        }
    
    return response

@mcp.tool()
def update_video(video_id: str, title: str = None, description: str = None, privacy: str = None) -> Dict:
    """
    Update video metadata
    
    Args:
        video_id: Video ID or URI
        title: New title (optional)
        description: New description (optional)
        privacy: New privacy setting (optional: public, unlisted, private, password)
        
    Returns:
        Updated video information
    """
    video_id = video_id.strip("/").split("/")[-1]
    
    data = {}
    if title is not None:
        data["name"] = title
    if description is not None:
        data["description"] = description
    if privacy is not None:
        data["privacy"] = {"view": privacy}
    
    if not data:
        return {"error": "No update parameters provided"}
    
    response = vimeo_request("PATCH", f"/videos/{video_id}", data=data)
    
    if "error" not in response:
        return {
            "success": True,
            "video_id": video_id,
            "message": "Video updated successfully",
            "updated_fields": list(data.keys())
        }
    
    return response

@mcp.tool()
def delete_video(video_id: str) -> Dict:
    """
    Delete a video from Vimeo
    
    Args:
        video_id: Video ID or URI
        
    Returns:
        Deletion status
    """
    video_id = video_id.strip("/").split("/")[-1]
    response = vimeo_request("DELETE", f"/videos/{video_id}")
    
    if "error" not in response:
        return {
            "success": True,
            "video_id": video_id,
            "message": f"Video {video_id} deleted successfully"
        }
    
    return response

# ===== FOLDER MANAGEMENT TOOLS =====

@mcp.tool()
def create_folder(name: str, parent_folder_uri: str = None) -> Dict:
    """
    Create a new folder for organizing videos
    
    Args:
        name: Folder name
        parent_folder_uri: Parent folder URI (optional)
        
    Returns:
        Created folder information
    """
    data = {"name": name}
    if parent_folder_uri:
        data["parent_folder_uri"] = parent_folder_uri
    
    response = vimeo_request("POST", "/me/folders", data=data)
    
    if "error" not in response and "uri" in response:
        response["folder_id"] = response["uri"].split("/")[-1]
        response["message"] = f"Folder '{name}' created successfully"
    
    return response

@mcp.tool()
def get_folders() -> Dict:
    """
    Get all folders for the authenticated user
    
    Returns:
        List of user's folders
    """
    response = vimeo_request("GET", "/me/folders")
    
    if "error" not in response and "data" in response:
        folders = []
        for folder in response.get("data", []):
            folders.append({
                "folder_id": folder.get("uri", "").split("/")[-1],
                "name": folder.get("name"),
                "created_time": folder.get("created_time"),
                "modified_time": folder.get("modified_time"),
                "video_count": folder.get("metadata", {}).get("connections", {}).get("videos", {}).get("total", 0)
            })
        
        return {
            "total": response.get("total", 0),
            "folders": folders
        }
    
    return response

@mcp.tool()
def add_video_to_folder(folder_id: str, video_id: str) -> Dict:
    """
    Add a video to a folder
    
    Args:
        folder_id: Folder ID or URI
        video_id: Video ID or URI
        
    Returns:
        Operation status
    """
    folder_id = folder_id.strip("/").split("/")[-1]
    video_id = video_id.strip("/").split("/")[-1]
    
    response = vimeo_request("PUT", f"/me/folders/{folder_id}/videos/{video_id}")
    
    if "error" not in response:
        return {
            "success": True,
            "message": f"Video {video_id} added to folder {folder_id}"
        }
    
    return response

@mcp.tool()
def remove_video_from_folder(folder_id: str, video_id: str) -> Dict:
    """
    Remove a video from a folder
    
    Args:
        folder_id: Folder ID or URI
        video_id: Video ID or URI
        
    Returns:
        Operation status
    """
    folder_id = folder_id.strip("/").split("/")[-1]
    video_id = video_id.strip("/").split("/")[-1]
    
    response = vimeo_request("DELETE", f"/me/folders/{folder_id}/videos/{video_id}")
    
    if "error" not in response:
        return {
            "success": True,
            "message": f"Video {video_id} removed from folder {folder_id}"
        }
    
    return response

@mcp.tool()
def get_folder_videos(folder_id: str, page: int = 1, per_page: int = 25) -> Dict:
    """
    Get videos in a specific folder
    
    Args:
        folder_id: Folder ID or URI
        page: Page number
        per_page: Number of items per page
        
    Returns:
        List of videos in the folder
    """
    folder_id = folder_id.strip("/").split("/")[-1]
    params = {
        "page": page,
        "per_page": min(per_page, 100)
    }
    
    response = vimeo_request("GET", f"/me/folders/{folder_id}/videos", params=params)
    
    if "error" not in response and "data" in response:
        videos = []
        for video in response.get("data", []):
            videos.append({
                "video_id": video.get("uri", "").split("/")[-1],
                "title": video.get("name"),
                "duration": video.get("duration"),
                "created_time": video.get("created_time"),
                "privacy": video.get("privacy", {}).get("view"),
                "status": video.get("transcode", {}).get("status", "unknown")
            })
        
        return {
            "folder_id": folder_id,
            "total": response.get("total", 0),
            "page": response.get("page", 1),
            "videos": videos
        }
    
    return response

# Test function to check API key
@mcp.tool()
def test_vimeo_connection() -> Dict:
    """
    Test if the Vimeo API key is working by making a simple request
    
    Returns:
        Connection test result
    """
    try:
        # Test with a simple user info request
        response = vimeo_request("GET", "/me")
        
        if "error" in response:
            return {
                "success": False,
                "error": response["error"],
                "suggestion": "Check your VIMEO_API_KEY and ensure it has proper scopes (public, private, edit, upload)"
            }
        
        return {
            "success": True,
            "user_name": response.get("name", "Unknown"),
            "account_type": response.get("account", "Unknown"),
            "message": "Vimeo API connection successful!",
            "available_scopes": response.get("metadata", {}).get("connections", {}).keys() if response.get("metadata") else []
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Connection test failed: {str(e)}",
            "suggestion": "Verify your VIMEO_API_KEY is correctly set in .env file"
        }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")






