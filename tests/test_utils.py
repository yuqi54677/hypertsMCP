"""Tests for utility functions."""
import pandas as pd
import pytest
from hypertsMCP.utils import is_nested, is_3d_array, df_to_json, json_to_df


class TestIsNested:
    """Tests for is_nested function."""
    
    def test_nested_dataframe(self, nested_dataframe):
        """Should detect nested structures in DataFrame."""
        assert is_nested(nested_dataframe) is True
    
    def test_regular_dataframe(self, regular_dataframe):
        """Should not detect nested structures in regular DataFrame."""
        assert is_nested(regular_dataframe) is False
    
    def test_simple_dataframe(self, sample_dataframe):
        """Should not detect nested structures in simple DataFrame."""
        assert is_nested(sample_dataframe) is False


class TestIs3DArray:
    """Tests for is_3d_array function."""
    
    def test_3d_numpy_array(self):
        """Should detect 3D numpy array."""
        import numpy as np
        arr = np.zeros((2, 3, 4))
        assert is_3d_array(arr) is True
    
    def test_2d_numpy_array(self):
        """Should not detect 2D numpy array as 3D."""
        import numpy as np
        arr = np.zeros((2, 3))
        assert is_3d_array(arr) is False
    
    def test_nested_list_3d(self):
        """Should detect 3D nested list structure."""
        arr = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
        assert is_3d_array(arr) is True
    
    def test_2d_list(self):
        """Should not detect 2D list as 3D."""
        arr = [[1, 2], [3, 4]]
        assert is_3d_array(arr) is False


class TestDataFrameJsonConversion:
    """Tests for DataFrame/JSON conversion functions."""
    
    def test_roundtrip_simple_dataframe(self, sample_dataframe):
        """Should preserve simple DataFrame through JSON conversion."""
        json_str = df_to_json(sample_dataframe)
        reconstructed = json_to_df(json_str)
        
        pd.testing.assert_frame_equal(sample_dataframe, reconstructed)
    
    def test_roundtrip_nested_dataframe(self, nested_dataframe):
        """Should preserve nested DataFrame through JSON conversion."""
        json_str = df_to_json(nested_dataframe)
        reconstructed = json_to_df(json_str)
        
        # Compare structure and values
        assert reconstructed.shape == nested_dataframe.shape
        assert list(reconstructed.columns) == list(nested_dataframe.columns)
        
        # Compare values (handling nested Series)
        for col in nested_dataframe.columns:
            for i in range(len(nested_dataframe)):
                val1 = nested_dataframe[col].iloc[i]
                val2 = reconstructed[col].iloc[i]
                
                if isinstance(val1, pd.Series):
                    val1 = val1.tolist()
                if isinstance(val2, pd.Series):
                    val2 = val2.tolist()
                
                if isinstance(val1, list) and isinstance(val2, list):
                    assert len(val1) == len(val2)
                    assert all(v1 == v2 for v1, v2 in zip(val1, val2))
                else:
                    assert val1 == val2
