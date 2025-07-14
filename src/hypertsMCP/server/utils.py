import pandas as pd
import numpy as np
from typing import Union, Any, Dict, List
import json
from datetime import datetime


def is_3d_array(arr: Union[np.ndarray, list]) -> bool:
    if isinstance(arr, np.ndarray):
        return arr.ndim == 3
    elif isinstance(arr, list):
        return (len(arr) > 0 and isinstance(arr[0], list) and 
                len(arr[0]) > 0 and isinstance(arr[0][0], list))
    return False

def is_nested(df: pd.DataFrame) -> bool:
    for col in df.columns:
        if df[col].apply(lambda x: isinstance(x, (list, dict, pd.Series, pd.DataFrame, np.ndarray))).any():
            return True
        if df[col].dtype == object and not df[col].apply(
            lambda x: isinstance(x, (str, int, float, bool)) or pd.isna(x)
        ).all():
            return True
    return False

def df_to_json(df):
    # 递归处理嵌套结构中的Series
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

def json_to_df(json_data):
    # 递归重建Series和DataFrame
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