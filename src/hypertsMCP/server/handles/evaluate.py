"""Handler for model evaluation functionality."""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from mcp import Tool
from .base import BaseHandler
from ..storage_manager import ModelStore
import pandas as pd
from ..utils import json_to_df, df_to_json
import numpy as np
class EvaluateArgs(BaseModel):
    test_data: str
    y_pred: List
    model_id: str  # ID of the model used for evaluation
    y_proba: Optional[dict] = None  # Optional predicted probabilities

class RunEvaluate(BaseHandler):
    name = "evaluate"
    description = "Evaluate model performance against test data."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=EvaluateArgs.model_json_schema()
        )
    
    async def handle_evaluate(self, args: EvaluateArgs) -> dict:
        """Evaluate model performance against test data."""
        test_df = json_to_df(args.test_data)
        y_pred = np.array(args.y_pred)
        y_proba_df = json_to_df(args.y_proba) if args.y_proba else None
        
        model = ModelStore.load(args.model_id)
        _, y_test = model.split_X_y(test_df.copy())
        scores = model.evaluate(y_test, y_pred, y_proba_df)
        scores_json = df_to_json(scores)

        return {'scores': scores_json}

    async def run_tool(self, arguments: Dict[str, Any]) -> dict:
        """Run the evaluate tool."""
        input_args = EvaluateArgs(**arguments)
        result = await self.handle_evaluate(input_args)
        return result