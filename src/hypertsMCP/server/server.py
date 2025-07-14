import asyncio
import contextlib
import os

from starlette.responses import Response

import uvicorn

from typing import Sequence, Dict, Any
from mcp.server.sse import SseServerTransport

from mcp.server.lowlevel import Server
from mcp.types import Tool, TextContent, Prompt, GetPromptResult

from fastapi import FastAPI

from starlette.applications import Starlette
from starlette.routing import Route, Mount

from handles.base import ToolRegistry

from starlette.requests import Request
from starlette.responses import JSONResponse

from storage_manager import storage

# initialize mcp lowlevel server, sse transport, and fastapi
mcp_app = Server("operateMysql")
fastapi_app = FastAPI()
sse = SseServerTransport("/messages/")

# MCP server handlers

#list available tools in mcp format
@mcp_app.list_tools()
async def list_tools() -> list[Tool]:
    return ToolRegistry.get_all_tools()

@mcp_app.call_tool()
async def call_tool(name: str, args: Dict[str, Any]) -> Sequence[TextContent]:
    tool = ToolRegistry.get_tool(name)
    return await tool.run_tool(args, 1)

#HTTP routes

# if no specific endpoint provided, list available tools
@fastapi_app.post("/")
async def root():
    return {"available http endpoints": ["train_test_split", "train_model", "predict", "evaluate"]}

# a method that auto register tools as fastapi routes, using tool name as endpoint
def register_fastapi_tool_route(app: FastAPI, tool_name: str):
    tool = ToolRegistry.get_tool(tool_name)

    @app.post(f"/{tool_name}")
    async def tool_route(args: Dict[str, Any]):
        return await tool.run_tool(args, 0)

# register tools for HTTP calls
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
