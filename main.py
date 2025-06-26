import contextlib
from fastapi import FastAPI
from fireflies_server import mcp as fireflies_mcp
from github_server import mcp as github_mcp  
from prd_server import mcp as prd_mcp
import os

# Create a combined lifespan to manage all session managers
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(fireflies_mcp.session_manager.run())
        await stack.enter_async_context(github_mcp.session_manager.run())
        await stack.enter_async_context(prd_mcp.session_manager.run())
        yield

app = FastAPI(lifespan=lifespan)
app.mount("/fireflies", fireflies_mcp.streamable_http_app())
app.mount("/github", github_mcp.streamable_http_app())
app.mount("/prd", prd_mcp.streamable_http_app())

PORT = os.environ.get("PORT", 10000)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=PORT)