"""Shared utilities for DataFrame/JSON conversion with nested Series support."""
import pandas as pd
import numpy as np
from typing import Union, Any, Dict, List
import json


def is_3d_array(arr: Union[np.ndarray, list]) -> bool:
    """Check if array is 3-dimensional."""
    if isinstance(arr, np.ndarray):
        return arr.ndim == 3
    elif isinstance(arr, list):
        return (len(arr) > 0 and isinstance(arr[0], list) and 
                len(arr[0]) > 0 and isinstance(arr[0][0], list))
    return False


def is_nested(df: pd.DataFrame) -> bool:
    """Check if DataFrame contains nested structures (Series, arrays, etc.)."""
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict, pd.Series, pd.DataFrame, np.ndarray))).any():
            return True
        if df[col].dtype == object and not df[col].apply(
            lambda x: isinstance(x, (str, int, float, bool)) or pd.isna(x)
        ).all():
            return True
    return False


def df_to_json(df: pd.DataFrame) -> str:
    """
    Convert DataFrame to JSON string, handling nested Series structures.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        JSON string representation
    """
    def convert_series(obj):
        if isinstance(obj, pd.Series):
            return {
                '__type__': 'series',
                'values': obj.tolist(),
                'index': obj.index.tolist(),
                'dtype': str(obj.dtype)
            }
        elif isinstance(obj, dict):
            return {k: convert_series(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_series(item) for item in obj]
        else:
            return obj
    
    return json.dumps(convert_series(df.to_dict()))


def json_to_df(json_data: str) -> pd.DataFrame:
    """
    Convert JSON string back to DataFrame, reconstructing nested Series.
    
    Args:
        json_data: JSON string to convert
        
    Returns:
        Reconstructed DataFrame
    """
    def convert_back(obj):
        if isinstance(obj, dict):
            if obj.get('__type__') == 'series':
                return pd.Series(obj['values'], index=obj['index'], dtype=obj['dtype'])
            else:
                return {k: convert_back(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_back(item) for item in obj]
        else:
            return obj
    
    data_dict = convert_back(json.loads(json_data))
    return pd.DataFrame(data_dict)
