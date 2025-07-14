import asyncio
import json
import pandas as pd
from typing import Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from hyperts.datasets import load_basic_motions
from utils import df_to_json, json_to_df


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None

    async def connect(self, server_url: str):
        """Connect to the MCP SSE server."""
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()
        print("Connected to MCP server.")
        tools = await self.session.list_tools()
        print("Available tools:", [t.name for t in tools.tools])

    async def run_pipeline(self):
        """Simulates an LLM orchestrating all four tools."""
        df = load_basic_motions()
        df_json = df_to_json(df)

        print("\n[1] Calling `train_test_split`...")
        res = await self.session.call_tool(
            name="train_test_split",
            arguments={"jsonData": df_json, "test_size": 0.3}
        )
        split = json.loads(res.content[0].text)
        train_df = json_to_df(split["train_set"])
        test_df = json_to_df(split["test_set"])

        print("[2] Calling `train_model`...")
        res = await self.session.call_tool(
            name="train_model",
            arguments={
                "jsonData": df_to_json(train_df),
                "task": "classification",
                "mode": "stats",
                "target": "target"
            }
        )
        modelid = json.loads(res.content[0].text)["model_id"]

        print("[3] Calling `predict`...")
        res = await self.session.call_tool(
            name="predict",
            arguments={
                "jsonData": df_to_json(test_df),
                "model_id": modelid
            }
        )
        y_pred = json.loads(res.content[0].text)["prediction"]

        print("[4] Calling `evaluate`...")
        res = await self.session.call_tool(
            name="evaluate",
            arguments={
                "jsonData": df_to_json(test_df),
                "y_pred": y_pred,
                "model_id": modelid
            }
        )

        print("\n[✅] Evaluation result:")
        print(res.content[0].text)

    async def cleanup(self):
        """Gracefully clean up resources."""
        if hasattr(self, "_session_context"):
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, "_streams_context"):
            await self._streams_context.__aexit__(None, None, None)


async def main():
    client = MCPClient()
    try:
        await client.connect("http://localhost:9000/mcp/sse")
        await client.run_pipeline()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
