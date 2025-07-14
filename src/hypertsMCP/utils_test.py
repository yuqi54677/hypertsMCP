import pandas as pd
import numpy as np
from datetime import datetime
import json
from utils import is_3d_array, is_nested, nested_to_dict, dict_to_nested, df_to_json, json_to_df
from hyperts.datasets import load_basic_motions
from hyperts.datasets import load_network_traffic

nested_df = load_basic_motions()
regular_df = load_network_traffic()

def run_full_test_cycle() -> bool:
    """
    运行完整的测试循环（转换->复原->比较）
    
    返回:
        bool: 所有测试是否通过
    """
    test_results = {}

    #_test_convert_series()
    
    test_results['is_nested'] = _test_is_nested()
    
    test_results['dict_roundtrip'] = _test_dict_roundtrip()
    
    # 测试3：JSON转换往返测试
    test_results['json_roundtrip'] = _test_json_roundtrip()
    
    # # 测试4：3D数组检测（如果存在）
    # test_results['3d_array_detection'] = self._test_3d_array_detection()
    
    # 汇总结果
    all_passed = all(test_results.values())
    print("\n测试结果汇总:")
    for test_name, passed in test_results.items():
        print(f"{test_name}: {'通过' if passed else '失败'}")
    
    return all_passed

def _compare_dataframes(df1: pd.DataFrame, df2: pd.DataFrame) -> bool:
    """
    Robust DataFrame comparison that handles nested Series by converting them to lists first.
    """
    if df1.shape != df2.shape:
        print(f"形状不同: {df1.shape} != {df2.shape}")
        return False
    
    for col in df1.columns:
        if col not in df2.columns:
            print(f"列 '{col}' 不存在于复原DataFrame中")
            return False
        
        for i in range(len(df1)):
            #print("\n"+str(i))
            val1, val2 = df1[col].iloc[i], df2[col].iloc[i]
            
            # Convert any Series to lists before comparison
            val1 = val1.tolist() if isinstance(val1, pd.Series) else val1
            val2 = val2.tolist() if isinstance(val2, pd.Series) else val2
            print(type(val1))
            
            # Handle list comparison (including nested lists from Series conversion)
            if isinstance(val1, list) and isinstance(val2, list):
                if len(val1) != len(val2):
                    print(f"行 {i} 列 '{col}' 列表长度不同")
                    return False
                for v1, v2 in zip(val1, val2):
                    if v1 != v2:
                        print(f"行 {i} 列 '{col}' 列表值不同")
                        return False
            
            # Handle other types
            elif val1 != val2:
                print(f"行 {i} 列 '{col}' 值不同: {val1} != {val2}")
                return False
    
    return True

def _test_convert_series():
    new_df = convert_series_to_lists(nested_df)
    for col in new_df.columns:
        print(type(new_df[col][0]))

def _test_is_nested() -> bool:
    print("\n=== test is nested ===")
    b1 = is_nested(nested_df)
    b2 = is_nested(regular_df)
    return (b1 and not b2)

def _test_dict_roundtrip() -> bool:
    print("\n=== test transfomr ===")
    try:
        print("\n=== transformed to dict ===")
        dict_data = nested_to_dict(nested_df)
        # print("转换后的字典结构示例:", dict_data[0] if dict_data else {})
        
        print("\n=== transformed to df ===")
        reconstructed_df = dict_to_nested(dict_data)
        
        print("\ncompare")
        are_equal = _compare_dataframes(nested_df, reconstructed_df)
        print(f"数据一致性: {'一致' if are_equal else '不一致'}")
        return are_equal
    except Exception as e:
        print(f"字典转换测试失败: {str(e)}")
        return False

def _test_json_roundtrip() -> bool:
    """测试JSON转换往返"""
    print("\n=== 测试3：JSON转换往返 ===")
    try:
        # 转换为JSON
        json_data = df_to_json(nested_df)
        print("JSON数据长度:", len(json_data))
        
        # 从JSON复原
        from_json_df = json_to_df(json_data)
        
        # 比较原始和复原后的DataFrame
        are_equal = _compare_dataframes(nested_df, from_json_df)
        print(f"数据一致性: {'一致' if are_equal else '不一致'}")
        return are_equal
    except Exception as e:
        print(f"JSON转换测试失败: {str(e)}")
        return False

# def _test_3d_array_detection(self) -> bool:
#     """测试3D数组检测"""
#     print("\n=== 测试4：3D数组检测 ===")
#     try:
#         # 在DataFrame中查找可能的3D数组
#         has_3d = False
#         for col in self.original_df.columns:
#             sample = self.original_df[col].iloc[0] if len(self.original_df) > 0 else None
#             if isinstance(sample, (np.ndarray, list)):
#                 is_3d = self.converter.is_3d_array(sample)
#                 if is_3d:
#                     has_3d = True
#                     print(f"列 '{col}' 包含3D数组")
        
#         if not has_3d:
#             print("未检测到3D数组 - 测试跳过")
#         return True  # 只要不报错就视为通过
#     except Exception as e:
#         print(f"3D数组检测失败: {str(e)}")
#         return False




# 使用示例
if __name__ == "__main__":
    run_full_test_cycle()