import pandas as pd
from typing import Optional, Any, Dict, Sequence
from pydantic import BaseModel, Field

from mcp import Tool
from mcp.types import TextContent

from .base import BaseHandler
from ..storage_manager import ModelStore

from utils import json_to_df

class PredictArgs(BaseModel):
    test_data: str = Field(..., alias="jsonData")
    model_id: str  # ID of the model to use for prediction
    proba: bool = False  # Whether to return probability estimates


class RunPredict(BaseHandler):
    name = "predict"
    description = "Make predictions using a trained model."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=PredictArgs.model_json_schema()
        )
    
    async def handle_predict(self, args: PredictArgs) -> dict:
        print("running handle_predict\n")
        test_df = json_to_df(args.test_data)
        model = ModelStore.load(args.model_id)
        X_test, y_test = model.split_X_y(test_df.copy())
        # print(args.model_id)
        # print(type(model))
        # print(type(X_test))
        prediction = model.predict(X_test)
        
            
        return {'prediction': prediction.tolist()}

    async def run_tool(self, arguments: Dict[str, Any]) -> Sequence[TextContent]:
        input = PredictArgs(**arguments)
        print(type(input))
        result = await self.handle_predict(input)
        return result
