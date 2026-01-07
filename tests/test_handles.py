"""Tests for handler functions."""
import pytest
import pandas as pd
from hyperts.datasets import load_basic_motions
from hypertsMCP.server.handles.train_test_split import RunSplit
from hypertsMCP.utils import df_to_json, json_to_df


@pytest.fixture
def split_handler():
    """Fixture providing train_test_split handler instance."""
    return RunSplit()


@pytest.fixture
def sample_data_for_split():
    """Fixture providing sample data for train_test_split testing."""
    df = load_basic_motions()
    return df_to_json(df.head(20))  # Use small subset for faster tests


class TestTrainTestSplit:
    """Tests for train_test_split handler."""
    
    @pytest.mark.asyncio
    async def test_basic_split(self, split_handler, sample_data_for_split):
        """Should split data into train and test sets."""
        result = await split_handler.run_tool({
            "data": sample_data_for_split,
            "test_size": 0.3,
            "random_state": 42
        })
        
        assert "train_set" in result
        assert "test_set" in result
        
        train_df = json_to_df(result["train_set"])
        test_df = json_to_df(result["test_set"])
        
        assert len(train_df) > 0
        assert len(test_df) > 0
        assert len(train_df) + len(test_df) == 20  # Total should match input
    
    @pytest.mark.asyncio
    async def test_split_preserves_structure(self, split_handler, sample_data_for_split):
        """Should preserve nested DataFrame structure in split."""
        original_df = json_to_df(sample_data_for_split)
        result = await split_handler.run_tool({
            "data": sample_data_for_split,
            "test_size": 0.3,
            "random_state": 42
        })
        
        train_df = json_to_df(result["train_set"])
        test_df = json_to_df(result["test_set"])
        
        # Check that columns are preserved
        assert list(train_df.columns) == list(original_df.columns)
        assert list(test_df.columns) == list(original_df.columns)
        
        # Check that structure type is preserved (nested if original was nested)
        # This is a basic check - full validation would require comparing values
