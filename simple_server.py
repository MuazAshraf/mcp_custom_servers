from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Simple")

@mcp.tool()
def hello() -> str:
    """Say hello"""
    return "Hello, world!"