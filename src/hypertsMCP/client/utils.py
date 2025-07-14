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

# def convert_series_to_lists(df: pd.DataFrame) -> pd.DataFrame:
#     """
#     Convert all Pandas Series in DataFrame cells to lists.
    
#     Parameters:
#         df: Input DataFrame that may contain Series in cells
        
#     Returns:
#         A new DataFrame where all Series have been converted to lists
#     """
#     # Create a copy to avoid modifying the original DataFrame
#     result_df = df.copy()
    
#     for column in result_df.columns:
#         # Check if column contains Series objects
#         if result_df[column].apply(lambda x: isinstance(x, pd.Series)).any():
#             print('found series\n')
#             # Convert Series to lists
#             result_df[column] = result_df[column].apply(
#                 lambda x: x.tolist() if isinstance(x, pd.Series) else x
#             )
#             print(type(result_df[column][0]))
        
#         # Handle case where elements might be lists containing Series
#         result_df[column] = result_df[column].apply(
#             lambda x: _deep_convert_series_to_lists(x)
#         )
    
#     return result_df
# def _deep_convert_series_to_lists(obj: Any) -> Any:
#     """
#     Recursively convert Series to lists in nested structures.
#     """
#     if isinstance(obj, pd.Series):
#         return obj.tolist()
#     elif isinstance(obj, dict):
#         return {k: _deep_convert_series_to_lists(v) for k, v in obj.items()}
#     elif isinstance(obj, (list, tuple)):
#         return [_deep_convert_series_to_lists(item) for item in obj]
#     return obj

# def nested_to_dict(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     def _convert(value: Any) -> Any:
#         if isinstance(value, pd.Series):
#             return value.tolist()
#         elif isinstance(value, pd.DataFrame):
#             return nested_to_dict(value)
#         elif isinstance(value, np.ndarray):
#             return value.tolist()
#         elif isinstance(value, (datetime, np.generic)):
#             return value.item() if isinstance(value, np.generic) else value.isoformat()
#         elif isinstance(value, dict):
#             return {k: _convert(v) for k, v in value.items()}
#         elif isinstance(value, (list, tuple)):
#             return [_convert(v) for v in value]
#         return value

#     return [{col: _convert(val) for col, val in record.items()} 
#             for record in df.to_dict(orient='records')]

# def df_to_json(df: pd.DataFrame) -> str:
#     return json.dumps(nested_to_dict(df))

# def dict_to_nested(data: List[Dict[str, Any]]) -> pd.DataFrame:
#     def _reconstruct(value: Any) -> Any:
#         if isinstance(value, dict):
#             return {k: _reconstruct(v) for k, v in value.items()}
#         elif isinstance(value, list):
#             # 判断是否是二维列表（矩阵）
#             if len(value) > 0 and all(isinstance(x, list) for x in value):
#                 return [np.array(sublist) if any(isinstance(i, (float, int)) for i in sublist) else sublist 
#                         for sublist in value]
#             return value
#         return value

#     # 先创建普通DataFrame
#     df = pd.DataFrame(data)
    
#     # 重建嵌套结构
#     for col in df.columns:
#         if df[col].apply(lambda x: isinstance(x, (dict, list))).any():
#             df[col] = df[col].apply(_reconstruct)
    
#     return df

# def json_to_df(json_str: str) -> pd.DataFrame:
#     return dict_to_nested(json.loads(json_str))

