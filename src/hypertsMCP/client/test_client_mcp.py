"""Example MCP client demonstrating the full ML pipeline."""
import asyncio
import json
from typing import Optional
from mcp import ClientSession
from mcp.client.sse import sse_client
from hyperts.datasets import load_basic_motions
from hypertsMCP.utils import df_to_json, json_to_df

class MCPChainClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.train_df = None
        self.test_df = None
        self.modelid = None
        self.y_pred = None

    async def connect(self, server_url: str):
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()
        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()
        await self.session.initialize()
        print("Connected to MCP server.")
        tools = await self.session.list_tools()
        print("Available tools:", [t.name for t in tools.tools])

    async def cleanup(self):
        if hasattr(self, "_session_context"):
            await self._session_context.__aexit__(None, None, None)
        if hasattr(self, "_streams_context"):
            await self._streams_context.__aexit__(None, None, None)

    async def run_chain(self):
        df = load_basic_motions()
        df_json = df_to_json(df)

        # 1. train_test_split
        if not self.confirm("Proceed to train_test_split?"):
            return
        print("[1] Calling train_test_split...")
        res = await self.session.call_tool(
            name="train_test_split",
            arguments={"data": df_json, "test_size": 0.3}
        )
        result = res.content[0].text
        result_dict = json.loads(result)
        self.train_df = json_to_df(result_dict['train_set'])
        self.test_df = json_to_df(result_dict['test_set'])
        self.train_df.to_csv('./temp_files/mcp_train_set.csv', encoding='UTF-8')
        self.test_df.to_csv('./temp_files/mcp_test_set.csv', encoding='UTF-8')
        print("data sets saved")

        # 2. train_model
        if not self.confirm("Proceed to train_model?"):
            return
        print("[2] Calling train_model...")
        res = await self.session.call_tool(
            name="train_model",
            arguments={
                "train_data": df_to_json(self.train_df),
                "task": "classification",
                "mode": "stats",
                "target": "target"
            }
        )
        self.modelid = json.loads(res.content[0].text)["model_id"]
        print("model id: ", self.modelid)

        # 3. predict
        if not self.confirm("Proceed to predict?"):
            return
        print("[3] Calling predict...")
        res = await self.session.call_tool(
            name="predict",
            arguments={
                "test_data": df_to_json(self.test_df),
                "model_id": self.modelid
            }
        )
        result = res.content[0].text
        result_dict = json.loads(result)
        self.y_pred = result_dict['prediction']
        print(self.y_pred)

        # 4. evaluate
        if not self.confirm("Proceed to evaluate?"):
            return
        print("[4] Calling evaluate...")
        res = await self.session.call_tool(
            name="evaluate",
            arguments={
                "test_data": df_to_json(self.test_df),
                "y_pred": self.y_pred,
                "model_id": self.modelid
            }
        )
        result = res.content[0].text
        result_dict = json.loads(result)
        eval = json_to_df(result_dict['scores'])
        print("\nEvaluation result:")
        print(eval)

    def confirm(self, prompt):
        ans = input(f"{prompt} (y/n): ").strip().lower()
        return ans == 'y'

async def main():
    client = MCPChainClient()
    try:
        await client.connect("http://localhost:9000/mcp/sse")
        await client.run_chain()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 