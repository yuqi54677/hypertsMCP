"""Main server with MCP and HTTP endpoints."""
import json
import starlette
from starlette.responses import Response
import uvicorn

from typing import Sequence, Dict, Any
from mcp.server.sse import SseServerTransport
from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent

from fastapi import FastAPI
from starlette.applications import Starlette
from starlette.routing import Route, Mount

from .handles.base import ToolRegistry

# Initialize MCP server, SSE transport, and FastAPI
mcp_app = Server("operateMysql")
fastapi_app = FastAPI()
sse = SseServerTransport("/messages/")

# MCP server handlers
@mcp_app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools in MCP format."""
    return ToolRegistry.get_all_tools()


@mcp_app.call_tool()
async def call_tool(name: str, args: Dict[str, Any]) -> Sequence[TextContent]:
    """Call a tool by name with arguments."""
    tool = ToolRegistry.get_tool(name)
    result = await tool.run_tool(args)
    # Convert dict result to TextContent for MCP protocol
    if isinstance(result, dict):
        return [TextContent(type="text", text=json.dumps(result))]
    return result


# HTTP routes
@fastapi_app.post("/")
async def root():
    """List available HTTP endpoints."""
    return {"available http endpoints": ["train_test_split", "train_model", "predict", "evaluate"]}


def register_fastapi_tool_route(app: FastAPI, tool_name: str):
    """Register a tool as a FastAPI route using the tool name as endpoint."""
    tool = ToolRegistry.get_tool(tool_name)

    @app.post(f"/{tool_name}")
    async def tool_route(args: Dict[str, Any]):
        return await tool.run_tool(args)


# Register tools for HTTP calls
register_fastapi_tool_route(fastapi_app, "train_test_split")
register_fastapi_tool_route(fastapi_app, "train_model")
register_fastapi_tool_route(fastapi_app, "predict")
register_fastapi_tool_route(fastapi_app, "evaluate")

def run_server():
    async def handle_sse(request):
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_app.run(streams[0], streams[1], mcp_app.create_initialization_options())
        return Response()
    mcp_subapp = Starlette(
        routes = [
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            Mount("/", app=mcp_app)
        ]
    )
    starlette_app = Starlette(
        routes=[
            Mount("/http", app=fastapi_app),
            Mount("/mcp", app=mcp_subapp)
        ]
    )


    uvicorn.run(starlette_app, host="0.0.0.0", port=9000)

if __name__ == "__main__":
    run_server()
