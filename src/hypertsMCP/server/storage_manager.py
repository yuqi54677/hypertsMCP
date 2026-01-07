"""Model storage management using local file system."""
import os
import uuid
import joblib


class ModelStore:
    """Store and retrieve trained models using local file system."""
    base_dir = "./src/hypertsMCP/server/models"

    @classmethod
    def save(cls, model) -> str:
        """Save a model to disk and return its unique ID."""
        os.makedirs(cls.base_dir, exist_ok=True)
        model_id = str(uuid.uuid4())
        path = os.path.join(cls.base_dir, f"{model_id}.pkl")
        joblib.dump(model, path)
        return model_id

    @classmethod
    def load(cls, model_id: str):
        """Load a model from disk by its ID."""
        path = os.path.join(cls.base_dir, f"{model_id}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model {model_id} not found")
        return joblib.load(path)

