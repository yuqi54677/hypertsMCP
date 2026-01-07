"""Pytest fixtures and configuration."""
import pytest
import pandas as pd
from hyperts.datasets import load_basic_motions, load_network_traffic


@pytest.fixture
def nested_dataframe():
    """Fixture providing a DataFrame with nested Series structures."""
    return load_basic_motions()


@pytest.fixture
def regular_dataframe():
    """Fixture providing a regular DataFrame without nested structures."""
    return load_network_traffic()


@pytest.fixture
def sample_dataframe():
    """Fixture providing a simple test DataFrame."""
    return pd.DataFrame({
        'col1': [1, 2, 3],
        'col2': ['a', 'b', 'c'],
        'col3': [1.1, 2.2, 3.3]
    })
