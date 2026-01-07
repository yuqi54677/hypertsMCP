"""Handler for model training functionality."""
from typing import Optional, Any, Dict, List, Literal
from pydantic import BaseModel, Field
from mcp import Tool
from .base import BaseHandler
from ..storage_manager import ModelStore
from hyperts import make_experiment
from ..utils import json_to_df, is_nested


TaskType = Literal[
    'forecast', 'classification', 'regression', 'detection',
    'univariate-forecast', 'multivariate-forecast', 
    'univariate-binaryclass', 'univariate-multiclass',
    'multivariate-binaryclass', 'multivariate-multiclass'
]

class TrainModelArgs(BaseModel):
    train_data: str
    task: TaskType

    eval_data: Optional[str] = None
    test_data: Optional[str] = None
    mode: str = "stats"
    max_trials: int = 50
    eval_size: float = 0.2
    cv: bool = False
    num_folds: int = 3
    ensemble_size: int = 10
    target: Optional[str] = None
    freq: Optional[str] = None
    timestamp: Optional[str] = None
    forecast_train_data_periods: Optional[int] = None
    forecast_drop_part_sample: bool = False
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    covariates: Optional[List[str]] = Field(
        default=None, 
        alias="covariables",
        description="column name of covariates"
    )
    dl_forecast_window: Optional[int] = None
    dl_forecast_horizon: int = 1
    contamination: float = 0.05
    id: Optional[str] = None
    searcher: Optional[Any] = None
    search_space: Optional[Any] = None
    search_callbacks: Optional[Any] = None
    searcher_options: Optional[Any] = None
    callbacks: Optional[Any] = None
    early_stopping_rounds: int = 20
    early_stopping_time_limit: int = 3600
    early_stopping_reward: Optional[float] = None
    reward_metric: Optional[str] = None
    optimize_direction: Optional[str] = None
    discriminator: Optional[Any] = None
    hyper_model_options: Optional[dict] = None
    tf_gpu_usage_strategy: int = 0
    tf_memory_limit: int = 2048
    final_retrain_on_wholedata: bool = True
    verbose: int = 1
    log_level: Optional[str] = None
    random_state: Optional[int] = None
    clear_cache: Optional[bool] = None
    columns: Optional[str] = None
    cells_as_array: bool = False


class RunTrainModel(BaseHandler):
    name = "train_model"
    description = "Train a machine learning model and return a model ID."

    def get_tool_description(self) -> Tool:
        return Tool(
            name=self.name,
            description=self.description,
            inputSchema=TrainModelArgs.model_json_schema()
        )
    
    async def handle_train_model(self, args: TrainModelArgs) -> dict:
        """Train a machine learning model using HyperTS."""
        train_df = json_to_df(args.train_data)
        if args.task in ("classification", "regression") and not is_nested(train_df):
            # Note: Non-nested data may need transformation for classification/regression tasks
            pass
        
        experiment = make_experiment(
            train_data=train_df.copy(),
            task=args.task,
            eval_data=args.eval_data,
            test_data=args.test_data,
            mode=args.mode,
            max_trials=args.max_trials,
            eval_size=args.eval_size,
            cv=args.cv,
            num_folds=args.num_folds,
            ensemble_size=args.ensemble_size,
            target=args.target,
            freq=args.freq,
            timestamp=args.timestamp,
            forecast_train_data_periods=args.forecast_train_data_periods,
            forecast_drop_part_sample=args.forecast_drop_part_sample,
            timestamp_format=args.timestamp_format,
            covariates=args.covariates,
            dl_forecast_window=args.dl_forecast_window,
            dl_forecast_horizon=args.dl_forecast_horizon,
            contamination=args.contamination,
            id=args.id,
            searcher=args.searcher,
            search_space=args.search_space,
            search_callbacks=args.search_callbacks,
            searcher_options=args.searcher_options,
            callbacks=args.callbacks,
            early_stopping_rounds=args.early_stopping_rounds,
            early_stopping_time_limit=args.early_stopping_time_limit,
            early_stopping_reward=args.early_stopping_reward,
            reward_metric=args.reward_metric,
            optimize_direction=args.optimize_direction,
            discriminator=args.discriminator,
            hyper_model_options=args.hyper_model_options,
            tf_gpu_usage_strategy=args.tf_gpu_usage_strategy,
            tf_memory_limit=args.tf_memory_limit,
            final_retrain_on_wholedata=args.final_retrain_on_wholedata,
            verbose=args.verbose,
            log_level=args.log_level,
            random_state=args.random_state,
            clear_cache=args.clear_cache
        )
        model = experiment.run()
        unique_id = ModelStore.save(model)
        return {"model_id": unique_id}

    async def run_tool(self, arguments: Dict[str, Any]) -> dict:
        args = TrainModelArgs(**arguments)
        result = await self.handle_train_model(args)
        return result
