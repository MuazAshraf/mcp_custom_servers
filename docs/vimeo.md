# Vimeo MCP Server Documentation

## Overview
The Vimeo MCP server provides tools for interacting with Vimeo's API to upload, manage, and organize videos. It supports video uploads, metadata management, and folder organization.

## Configuration
Set the following environment variables in `.env`:

```bash
VIMEO_API_KEY=your-vimeo-api-key
ACCESS_TOKEN=your-vimeo-access-token
```

## Endpoints / Tools

### Video Upload Tools

#### 1. upload_video_tus
Upload a video to Vimeo using TUS protocol (for large files).

**Parameters:**
- `file_path` (string, required): Absolute path to the video file
- `title` (string, optional): Video title
- `description` (string, optional): Video description
- `privacy` (string, optional): Privacy setting (default: "unlisted")
  - Options: "public", "unlisted", "private", "password"

**Example Request:**
```json
{
  "tool_name": "upload_video_tus",
  "arguments": {
    "file_path": "/path/to/video.mp4",
    "title": "My Video Title",
    "description": "A description of my video",
    "privacy": "unlisted"
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "video_uri": "/videos/123456789",
  "video_id": "123456789",
  "upload_status": "complete",
  "title": "My Video Title",
  "message": "Video uploaded successfully. Processing may take a few minutes."
}
```

#### 2. upload_video_from_url
Upload a video to Vimeo from a URL (pull upload).

**Parameters:**
- `url` (string, required): HTTPS URL of the video file
- `title` (string, required): Video title
- `description` (string, optional): Video description
- `privacy` (string, optional): Privacy setting (default: "unlisted")

**Example Request:**
```json
{
  "tool_name": "upload_video_from_url",
  "arguments": {
    "url": "https://example.com/video.mp4",
    "title": "Video from URL",
    "description": "Uploaded from external URL",
    "privacy": "private"
  }
}
```

### Video Management Tools

#### 3. get_my_videos
Get authenticated user's videos.

**Parameters:**
- `page` (integer, optional): Page number (default: 1)
- `per_page` (integer, optional): Number of items per page (max 100, default: 25)
- `sort` (string, optional): Sort field (default: "date")
  - Options: "date", "alphabetical", "plays", "likes", "comments", "duration"
- `direction` (string, optional): Sort direction (default: "desc")
  - Options: "asc", "desc"

**Example Request:**
```json
{
  "tool_name": "get_my_videos",
  "arguments": {
    "page": 1,
    "per_page": 50,
    "sort": "plays",
    "direction": "desc"
  }
}
```

**Example Response:**
```json
{
  "total": 150,
  "page": 1,
  "per_page": 50,
  "videos": [
    {
      "video_id": "123456789",
      "title": "My Video",
      "description": "Video description",
      "duration": 120,
      "created_time": "2024-01-15T10:00:00+00:00",
      "privacy": "unlisted",
      "link": "https://vimeo.com/123456789",
      "plays": 1500,
      "status": "available"
    }
  ]
}
```

#### 4. get_video_details
Get detailed information about a specific video.

**Parameters:**
- `video_id` (string, required): Video ID or URI (e.g., "123456789" or "/videos/123456789")

**Example Request:**
```json
{
  "tool_name": "get_video_details",
  "arguments": {
    "video_id": "123456789"
  }
}
```

#### 5. update_video
Update video metadata.

**Parameters:**
- `video_id` (string, required): Video ID or URI
- `title` (string, optional): New title
- `description` (string, optional): New description
- `privacy` (string, optional): New privacy setting

**Example Request:**
```json
{
  "tool_name": "update_video",
  "arguments": {
    "video_id": "123456789",
    "title": "Updated Title",
    "description": "Updated description",
    "privacy": "public"
  }
}
```

#### 6. delete_video
Delete a video from Vimeo.

**Parameters:**
- `video_id` (string, required): Video ID or URI

**Example Request:**
```json
{
  "tool_name": "delete_video",
  "arguments": {
    "video_id": "123456789"
  }
}
```

### Folder Management Tools

#### 7. create_folder
Create a new folder for organizing videos.

**Parameters:**
- `name` (string, required): Folder name
- `parent_folder_uri` (string, optional): Parent folder URI

**Example Request:**
```json
{
  "tool_name": "create_folder",
  "arguments": {
    "name": "My Video Collection"
  }
}
```

#### 8. get_folders
Get all folders for the authenticated user.

**Parameters:** None

**Example Request:**
```json
{
  "tool_name": "get_folders",
  "arguments": {}
}
```

**Example Response:**
```json
{
  "total": 5,
  "folders": [
    {
      "folder_id": "987654321",
      "name": "My Video Collection",
      "created_time": "2024-01-10T08:00:00+00:00",
      "modified_time": "2024-01-15T10:30:00+00:00",
      "video_count": 25
    }
  ]
}
```

#### 9. add_video_to_folder
Add a video to a folder.

**Parameters:**
- `folder_id` (string, required): Folder ID or URI
- `video_id` (string, required): Video ID or URI

**Example Request:**
```json
{
  "tool_name": "add_video_to_folder",
  "arguments": {
    "folder_id": "987654321",
    "video_id": "123456789"
  }
}
```

## Video Privacy Settings

- **public**: Anyone can view the video
- **unlisted**: Only people with the link can view
- **private**: Only you can view the video
- **password**: Viewers need a password to watch

## Video Upload Status

When uploading videos, the transcode status indicates processing state:
- **in_progress**: Video is being processed
- **complete**: Video is ready to view
- **error**: Processing failed

## Testing with cURL

### Base URL
```
http://localhost:8000/mcp/call_tool
```

### Example: Get My Videos
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_my_videos",
    "arguments": {
      "per_page": 10,
      "sort": "date"
    }
  }'
```

### Example: Upload Video from URL
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "upload_video_from_url",
    "arguments": {
      "url": "https://example.com/sample-video.mp4",
      "title": "Sample Video",
      "privacy": "unlisted"
    }
  }'
```

### Example: Create Folder
```bash
curl -X POST http://localhost:8000/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "create_folder",
    "arguments": {
      "name": "2024 Videos"
    }
  }'
```

## Notes
- Large video uploads use the TUS protocol for resumable uploads
- Video processing after upload may take several minutes
- The API uses pagination for listing videos (max 100 per page)
- Rate limits apply based on your Vimeo plan
- Video IDs can be used with or without the "/videos/" prefix