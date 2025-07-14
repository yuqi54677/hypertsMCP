import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client

from dotenv import load_dotenv
import httpx

from hyperts.datasets import load_basic_motions
import pandas as pd

from utils import json_to_df, df_to_json
# from handles.train_test_split import SplitArgs
# from sklearn.model_selection import train_test_split
# from mcp.types import CallToolResult
# from mcp.types import CallToolRequest

load_dotenv()  # load environment variables from .env

class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def cleanup(self):
        """确保所有资源被正确释放"""
        # 取消所有后台任务
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
                try:
                    await task
                except (asyncio.CancelledError, Exception):
                    pass
        
        # 关闭SSE连接
        if hasattr(self, '_sse_client') and self._sse_client:
            await self._sse_client.close()
        
        # 关闭HTTP会话
        if hasattr(self, '_http_session') and self._http_session:
            await self._http_session.close()
        
        # 重置状态
        self._sse_client = None
        self._http_session = None


    async def test_mcp_loop(self):
        df = load_basic_motions()
        df.to_csv('./original.csv', encoding='UTF-8')
        train_df = None
        test_df = None
        modelid = None
        y_pred = None
        print("\nMCP Client Started!")
        while True:
            try:
                case = input("\ntest case: ").strip()
                if case== '1':
                    print("Calling train_test_split")
                    # df_json = df.to_dict(orient='records')
                    df_json = df_to_json(df)
                    print(type(df_json))
                    response = await self.session.call_tool(
                        name="train_test_split",
                        arguments={
                            "jsonData": df_json,
                            "test_size": 0.3
                        }
                    )
                    # extract df from response
                    result = response.content[0].text
                    print(result)
                    result_dict = json.loads(s=result)
                    print(type(result_dict['train_set']))
                    print(type(result_dict['test_set']))
                    train_df = json_to_df(result_dict['train_set'])
                    test_df = json_to_df(result_dict['test_set'])
                    print(type(train_df['Var_1'][0]))
                    # result_dict = json.loads(s=result)mc
                    # train_df = pd.DataFrame.from_dict(result_dict['train_set'])
                    # test_df = pd.DataFrame.from_dict(result_dict['test_set'])
                    train_df.to_csv('./train_set.csv', encoding='UTF-8')
                    test_df.to_csv('./test_set.csv', encoding='UTF-8')
                    print("data sets saved")
                
                if case=='2':
                    print("Calling train_model")
                    if train_df is not None:
                        train_json = df_to_json(train_df)
                    else:
                        train_json = df_to_json(df)
                    response = await self.session.call_tool(
                        name="train_model",
                        arguments={
                            "jsonData": train_json,
                            "task": 'classification',
                            "mode":'stats',
                            "target":'target'
                        }
                    )
                    result = response.content[0].text
                    print(result)
                    result_dict = json.loads(s=result)
                    modelid = result_dict['model_id']
                
                if case=='3':
                    print("Calling predict")
                    if test_df is not None:
                        test_json = df_to_json(test_df)
                    else:
                        test_json = df_to_json(df)
                    response = await self.session.call_tool(
                        name="predict",
                        arguments={
                            "jsonData": test_json,
                            "model_id": modelid
                        }
                    )
                    result = response.content[0].text
                    print(result)
                    result_dict = json.loads(s=result)
                    y_pred = result_dict['prediction']
                
                if case=='4':
                    print("Calling evaluate")
                    if test_df is not None:
                        test_json = df_to_json(test_df)
                    else:
                        test_json = df_to_json(df)
                    response = await self.session.call_tool(
                        name="evaluate",
                        arguments={
                            "jsonData": test_json,
                            "y_pred": y_pred,
                            "model_id": modelid
                        }
                    )
                    print(response)
                    print(response.content[0].text)

                if case.lower() == 'quit':
                    break
                #print(response.content[0].text)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")

    async def test_http_loop(self):
        print("\n HTTP Client Started!")
        base_url = "http://localhost:9000/http/"
        while True:
            try:
                tool = input("\ntool: ").strip()
                url = base_url+tool
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json={"data": {"x": [1, 2], "y": [2, 4]}, "test_size": 0.3})
                    print(response.json())
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    

async def main():

    client = MCPClient()
    try:
        case = input("\nmode: ").strip()
        if case=='mcp':
            await client.connect_to_sse_server(server_url="http://localhost:9000/mcp/sse")
            await client.test_mcp_loop()
        elif case=='http':
            await client.test_http_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    import sys
    asyncio.run(main())