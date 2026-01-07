"""Base handler and tool registry for MCP tools."""
from typing import Dict, Any, Type, ClassVar
from mcp.types import Tool


class ToolRegistry:
    _tools: ClassVar[Dict[str, 'BaseHandler']] = {}

    @classmethod
    def register(cls, tool_class: Type['BaseHandler']) -> Type['BaseHandler']:
        tool = tool_class()
        cls._tools[tool.name] = tool
        return tool_class

    @classmethod
    def get_tool(cls, name: str) -> 'BaseHandler':
        if name not in cls._tools:
            raise ValueError(f"invalid tool: {name}")
        return cls._tools[name]

    @classmethod
    def get_all_tools(cls) -> list[Tool]:
        return [tool.get_tool_description() for tool in cls._tools.values()]


class BaseHandler:
    name: str = ""
    description: str = ""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.name:
            ToolRegistry.register(cls)

    def get_tool_description(self) -> Tool:
        raise NotImplementedError

    async def run_tool(self, arguments: Dict[str, Any]):
        """Run the tool with given arguments. Returns dict for HTTP, or Sequence[TextContent] for MCP."""
        raise NotImplementedError

