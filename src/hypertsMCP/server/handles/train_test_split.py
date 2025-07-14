from typing import Dict, Any, Sequence, Optional, List, Union
from pydantic import BaseModel, Field, constr
from mcp import Tool
from mcp.types import TextContent
import pandas as pd
from sklearn.model_selection import train_test_split
from ..utils import df_to_json, json_to_df
# from ..storage_manager import storage
from .base import BaseHandler


class SplitArgs(BaseModel):
    data: str
    test_size: Optional[Union[float, int]] = None
    train_size: Optional[Union[float, int]] = None
    random_state: Optional[int] = None
    shuffle: bool = True
    stratify: Optional[List[Any]] = None


class RunSplit(BaseHandler):
    name = "train_test_split"
    description = "Split input data into train/test sets using scikit-learn."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=SplitArgs.model_json_schema()
        )
    
    async def handle_train_test_split(self, args: SplitArgs) -> dict:
        print("running handle_train_test_split\n")
        data_df = json_to_df(args.data)
        train_set, test_set = train_test_split(
            data_df,
            test_size=args.test_size,
            train_size=args.train_size,
            random_state=args.random_state,
            shuffle=args.shuffle,
            stratify=args.stratify
        )
        # train_set_json=train_set.to_dict(orient='records')
        # test_set_json=test_set.to_dict(orient='records')
        train_set_json = df_to_json(train_set)
        test_set_json = df_to_json(test_set)
        return {"train_set":train_set_json, "test_set":test_set_json}

    async def run_tool(self, arguments: Dict[str, Any]) -> dict:
        print("run_tool for train_test_split\n")
        print(type(arguments["data"]))
        input = SplitArgs(**arguments)
        print(isinstance(input.data, str))
        print(isinstance(input.data, List))
        print(isinstance(input.data, Dict))
        print(type(input))
        result = await self.handle_train_test_split(input)
        return result
