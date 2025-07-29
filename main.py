from fastapi import FastAPI
from fireflies_server import mcp as fireflies_mcp
from github_server import mcp as github_mcp  
from prd_server import mcp as prd_mcp
from vimeo_server import mcp as vimeo_mcp
import os

# Create FastAPI app
app = FastAPI()

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "MCP Hub is running"}

# Mount the MCP servers directly - they handle their own initialization
app.mount("/fireflies", fireflies_mcp.streamable_http_app())
app.mount("/github", github_mcp.streamable_http_app())
app.mount("/prd", prd_mcp.streamable_http_app())
app.mount("/vimeo", vimeo_mcp.streamable_http_app())

PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)