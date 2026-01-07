"""Backward compatibility: re-export shared utils."""
from ..utils import (
    is_3d_array,
    is_nested,
    df_to_json,
    json_to_df
)

__all__ = ['is_3d_array', 'is_nested', 'df_to_json', 'json_to_df']

