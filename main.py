import contextlib
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv('.env')

# Import MCP instances from each server file
from fireflies_server import mcp as fireflies_mcp
from github_server import mcp as github_mcp  
from prd_server import mcp as prd_mcp

# Create a combined lifespan to manage all session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(fireflies_mcp.session_manager.run())
        await stack.enter_async_context(github_mcp.session_manager.run())
        await stack.enter_async_context(prd_mcp.session_manager.run())
        yield

# Create FastAPI application
app = FastAPI(
    title="MCP Servers Hub",
    description="Multiple MCP servers mounted on FastAPI",
    version="1.0.0",
    lifespan=lifespan
)

# Mount each MCP server on different paths
app.mount("/fireflies", fireflies_mcp.streamable_http_app())
app.mount("/github", github_mcp.streamable_http_app())
app.mount("/prd", prd_mcp.streamable_http_app())

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "message": "MCP Servers Hub is running",
        "servers": {
            "fireflies": "http://YOUR-SERVER-IP:8000/fireflies/mcp/",
            "github": "http://YOUR-SERVER-IP:8000/github/mcp/",
            "prd": "http://YOUR-SERVER-IP:8000/prd/mcp/"
        },
        "status": "active"
    }

if __name__ == "__main__":
    host = os.getenv('MCP_HOST', '0.0.0.0')
    port = int(os.getenv('MCP_PORT', 8000))
    uvicorn.run(app, host=host, port=port, log_level="info") 