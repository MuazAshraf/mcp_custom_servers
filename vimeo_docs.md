📤 Video Upload Tools

  1. upload_video_tus (For large files)

  # Required params:
  file_path = "/path/to/your/video.mp4"  # Absolute path

  # Optional params:
  title = "My Amazing Video"
  description = "This is a great video"
  privacy = "unlisted"  # Options: "public", "unlisted", "private", "password"     

  # Example call:
  upload_video_tus(
      file_path="/Users/you/Desktop/video.mp4",
      title="Product Demo 2025",
      description="Our latest product features",
      privacy="unlisted"
  )

  2. upload_video_from_url

  # Required params:
  url = "https://example.com/video.mp4"  # Must be HTTPS
  title = "Downloaded Video"

  # Optional params:
  description = "Video from external source"
  privacy = "private"

  # Example call:
  upload_video_from_url(
      url="https://storage.example.com/demo.mp4",
      title="Conference Recording",
      description="Annual conference 2025",
      privacy="private"
  )

  📹 Video Management Tools

  3. get_my_videos

  # All params optional:
  page = 1  # Page number
  per_page = 25  # Items per page (max 100)
  sort = "date"  # Options: "date", "alphabetical", "plays", "likes", 
  "comments", "duration"
  direction = "desc"  # Options: "asc", "desc"

  # Example call:
  get_my_videos(page=1, per_page=50, sort="plays", direction="desc")

  4. get_video_details

  # Required param:
  video_id = "123456789"  # Just the numeric ID or full URI 
  "/videos/123456789"

  # Example call:
  get_video_details("987654321")

  5. update_video

  # Required param:
  video_id = "123456789"

  # At least one optional param required:
  title = "New Title"
  description = "Updated description"
  privacy = "public"  # Options: "public", "unlisted", "private", "password"       

  # Example call:
  update_video(
      video_id="123456789",
      title="Updated Product Demo",
      privacy="public"
  )

  6. delete_video

  # Required param:
  video_id = "123456789"

  # Example call:
  delete_video("123456789")

  📁 Folder Management Tools

  7. create_folder

  # Required param:
  name = "My Videos"

  # Optional param:
  parent_folder_uri = "/users/12345/folders/67890"  # For nested folders

  # Example call:
  create_folder(name="Marketing Videos 2025")

  8. get_folders

  # No params required
  get_folders()

  9. add_video_to_folder

  # Required params:
  folder_id = "12345"
  video_id = "67890"

  # Example call:
  add_video_to_folder(folder_id="999888", video_id="777666")

  10. remove_video_from_folder

  # Required params:
  folder_id = "12345"
  video_id = "67890"

  # Example call:
  remove_video_from_folder(folder_id="999888", video_id="777666")

  11. get_folder_videos

  # Required param:
  folder_id = "12345"

  # Optional params:
  page = 1
  per_page = 25

  # Example call:
  get_folder_videos(folder_id="999888", page=1, per_page=50)

  🚀 Complete Usage Example

  # 1. Upload a video
  result = upload_video_tus(
      file_path="/home/user/video.mp4",
      title="My Tutorial",
      description="Learn how to use our app",
      privacy="unlisted"
  )
  video_id = result["video_id"]  # Save this!

  # 2. Check upload status
  status = get_video_details(video_id)
  print(f"Transcode status: {status['transcode_status']}")

  # 3. Create a folder
  folder_result = create_folder(name="Tutorials 2025")
  folder_id = folder_result["folder_id"]

  # 4. Add video to folder
  add_video_to_folder(folder_id=folder_id, video_id=video_id)

  # 5. Update video metadata
  update_video(
      video_id=video_id,
      title="Updated Tutorial - Final Version",
      privacy="public"
  )

  # 6. List all videos
  my_videos = get_my_videos(sort="date", direction="desc")
  print(f"Total videos: {my_videos['total']}")

  🔑 Important Notes

  1. Video IDs: Can be passed as just the numeric ID ("123456789") or full URI     
   ("/videos/123456789")
  2. Privacy Options: "public", "unlisted", "private", "password"
  3. File Paths: Must be absolute paths when uploading
  4. Upload Status: After upload, videos need time to transcode. Check
  transcode_status to see if ready
  5. Pagination: Most list endpoints support page and per_page parameters