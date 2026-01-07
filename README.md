# HyperTS MCP Server

A Model Context Protocol (MCP) server that provides time series machine learning capabilities through both MCP protocol and HTTP REST API. Built on top of [HyperTS](https://github.com/DataCanvasIO/HyperTS), this server enables automated time series forecasting, classification, and regression tasks.

## Features

- 🔄 **Dual Protocol Support**: Access via MCP protocol (SSE) or HTTP REST API
- 📊 **Time Series ML**: Supports forecasting, classification, and regression tasks
- 🧩 **Nested DataFrame Support**: Handles complex nested data structures with Series
- 🔧 **Complete ML Pipeline**: Train/test split, model training, prediction, and evaluation
- 💾 **Model Persistence**: Automatic model storage and retrieval via unique IDs
- ✅ **Well-Tested**: Professional pytest test suite with fixtures

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yuqi54677/hypertsMCP.git
cd hypertsMCP
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Quick Start

### Starting the Server

Run the server from the project root:

```bash
python main.py
```

The server will start on `http://0.0.0.0:9000` with:
- **MCP Protocol**: Available at `http://localhost:9000/mcp/sse`
- **HTTP API**: Available at `http://localhost:9000/http/`

### Available Endpoints

The server provides the following tools/endpoints:

1. **train_test_split** - Split data into training and test sets
2. **train_model** - Train a time series ML model
3. **predict** - Make predictions using a trained model
4. **evaluate** - Evaluate model performance

## Usage

### HTTP API Example

See `src/hypertsMCP/client/test_client_http.py` for a complete example. Basic usage:

```python
import httpx
import asyncio
from hyperts.datasets import load_basic_motions
from hypertsMCP.utils import df_to_json, json_to_df

async def main():
    df = load_basic_motions()
    df_json = df_to_json(df)
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        base_url = "http://localhost:9000/http/"
        
        # 1. Split data
        res = await client.post(
            f"{base_url}train_test_split",
            json={"data": df_json, "test_size": 0.3}
        )
        result = res.json()
        train_df = json_to_df(result['train_set'])
        test_df = json_to_df(result['test_set'])
        
        # 2. Train model
        res = await client.post(
            f"{base_url}train_model",
            json={
                "train_data": df_to_json(train_df),
                "task": "classification",
                "mode": "stats",
                "target": "target"
            }
        )
        model_id = res.json()["model_id"]
        
        # 3. Predict
        res = await client.post(
            f"{base_url}predict",
            json={
                "test_data": df_to_json(test_df),
                "model_id": model_id
            }
        )
        predictions = res.json()['prediction']
        
        # 4. Evaluate
        res = await client.post(
            f"{base_url}evaluate",
            json={
                "test_data": df_to_json(test_df),
                "y_pred": predictions,
                "model_id": model_id
            }
        )
        scores = json_to_df(res.json()['scores'])
        print(scores)

asyncio.run(main())
```

### MCP Protocol Example

See `src/hypertsMCP/client/test_client_mcp.py` for a complete MCP client example.

## API Reference

### train_test_split

Split input data into training and test sets.

**Parameters:**
- `data` (str): JSON string representation of DataFrame
- `test_size` (float, optional): Proportion of dataset to include in test split
- `train_size` (float, optional): Proportion of dataset to include in train split
- `random_state` (int, optional): Random seed for reproducibility
- `shuffle` (bool): Whether to shuffle data before splitting (default: True)
- `stratify` (list, optional): For stratified splitting

**Returns:**
```json
{
  "train_set": "<JSON string>",
  "test_set": "<JSON string>"
}
```

### train_model

Train a time series machine learning model.

**Parameters:**
- `train_data` (str): JSON string representation of training DataFrame
- `task` (str): Task type - one of: `forecast`, `classification`, `regression`, `detection`, etc.
- `mode` (str): Training mode (default: "stats")
- `target` (str, optional): Target column name
- `max_trials` (int): Maximum number of trials (default: 50)
- ... (many other optional parameters)

**Returns:**
```json
{
  "model_id": "<unique-model-id>"
}
```

### predict

Make predictions using a trained model.

**Parameters:**
- `test_data` (str): JSON string representation of test DataFrame
- `model_id` (str): ID of the trained model
- `proba` (bool): Whether to return probability estimates (default: False)

**Returns:**
```json
{
  "prediction": [<array of predictions>]
}
```

### evaluate

Evaluate model performance.

**Parameters:**
- `test_data` (str): JSON string representation of test DataFrame
- `y_pred` (list): Predicted values
- `model_id` (str): ID of the model used for prediction
- `y_proba` (dict, optional): Predicted probabilities

**Returns:**
```json
{
  "scores": "<JSON string of evaluation metrics DataFrame>"
}
```

## Project Structure

```
hypertsMCP/
├── src/
│   └── hypertsMCP/
│       ├── utils.py              # Shared utilities for DataFrame/JSON conversion
│       ├── server/
│       │   ├── server.py         # Main server with MCP and HTTP handlers
│       │   ├── storage_manager.py # Model persistence
│       │   ├── utils.py          # Server utilities (re-exports from shared)
│       │   └── handles/          # Tool handlers
│       │       ├── base.py       # Base handler and registry
│       │       ├── train_test_split.py
│       │       ├── train_model.py
│       │       ├── predict.py
│       │       └── evaluate.py
│       └── client/
│           ├── test_client_mcp.py   # MCP client example
│           ├── test_client_http.py  # HTTP client example
│           └── utils.py             # Client utilities (re-exports from shared)
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_utils.py            # Tests for utility functions
│   └── test_handles.py          # Tests for handlers
├── main.py                      # Server entry point
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
└── README.md                    # This file
```

## Testing

Run the test suite:

```bash
pytest
```

Run specific test files:

```bash
pytest tests/test_utils.py
pytest tests/test_handles.py
```

## Utilities

The project includes utilities for handling nested DataFrame structures:

- `df_to_json(df)`: Convert DataFrame to JSON string, preserving nested Series
- `json_to_df(json_str)`: Convert JSON string back to DataFrame
- `is_nested(df)`: Check if DataFrame contains nested structures
- `is_3d_array(arr)`: Check if array is 3-dimensional

These utilities properly handle pandas Series objects within DataFrames, making them ideal for time series data with nested structures.

## Requirements

- Python 3.7+
- See `requirements.txt` for full dependency list

Key dependencies:
- `hyperts` - Time series machine learning library
- `mcp` - Model Context Protocol
- `fastapi` - HTTP API framework
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `scikit-learn` - Machine learning utilities

## License

See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure tests pass before submitting PRs.

## Notes

- Models are stored locally in `src/hypertsMCP/server/models/`
- The server uses joblib for model serialization
- Nested DataFrame structures are fully supported through custom JSON serialization
- Both MCP and HTTP interfaces share the same underlying handlers
