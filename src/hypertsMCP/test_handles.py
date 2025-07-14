from handles.train_test_split import RunSplit, SplitArgs
from handles.train_model import RunTrainModel, TrainModelArgs
from handles.predict import RunPredict, PredictArgs
from handles.evaluate import RunEvaluate, EvaluateArgs

from hyperts.datasets import load_random_univariate_forecast_dataset


# conftest.py
import pytest
import pandas as pd

@pytest.fixture
def train_test_split_test_cases():
    load_random_univariate_forecast_dataset.
    return [
        {
            "input": ("Alice", 20, [70, 80, 90]),
            "expected": pd.DataFrame({
                'name': ['Alice'],
                'age': [20],
                'avg_score': [80.0],
                'passed': [True]
            })
        },
        {
            "input": ("Bob", 18, [55, 65]),
            "expected": pd.DataFrame({
                'name': ['Bob'],
                'age': [18],
                'avg_score': [60.0],
                'passed': [True]
            })
        }
    ]

# test_file.py
def test_with_fixture(sample_test_cases):
    for case in sample_test_cases:
        result = process_data(*case["input"])
        pd.testing.assert_frame_equal(result, case["expected"])