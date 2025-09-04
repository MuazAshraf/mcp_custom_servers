from fastapi import FastAPI
from fireflies_server import mcp as fireflies_mcp
from github_server import mcp as github_mcp  
from prd_server import mcp as prd_mcp
from vimeo_server import mcp as vimeo_mcp
from mailgun_server import mcp as mailgun_mcp
from dashboard_server import mcp as dashboard

import os
import contextlib

# Create a combined lifespan to manage all session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        # Initialize all session managers
        await stack.enter_async_context(fireflies_mcp.session_manager.run())
        await stack.enter_async_context(github_mcp.session_manager.run())
        await stack.enter_async_context(prd_mcp.session_manager.run())
        await stack.enter_async_context(vimeo_mcp.session_manager.run())
        await stack.enter_async_context(mailgun_mcp.session_manager.run())
        await stack.enter_async_context(dashboard.session_manager.run())
        yield

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Add a health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "MCP Hub is running"}

# Mount the MCP servers
app.mount("/fireflies", fireflies_mcp.streamable_http_app())
app.mount("/github", github_mcp.streamable_http_app())
app.mount("/prd", prd_mcp.streamable_http_app())
app.mount("/vimeo", vimeo_mcp.streamable_http_app())
app.mount("/mailgun", mailgun_mcp.streamable_http_app())
app.mount("/dashboard", dashboard.streamable_http_app())


PORT = int(os.environ.get("PORT", 8000))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)