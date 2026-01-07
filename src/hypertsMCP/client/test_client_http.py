"""Example HTTP client demonstrating the full ML pipeline."""
import asyncio
import httpx
from hyperts.datasets import load_basic_motions
from hypertsMCP.utils import df_to_json, json_to_df

class HTTPChainClient:
    def __init__(self):
        self.train_df = None
        self.test_df = None
        self.modelid = None
        self.y_pred = None
        self.base_url = "http://localhost:9000/http/"

    async def run_chain(self):
        df = load_basic_motions()
        df_json = df_to_json(df)
        async with httpx.AsyncClient(timeout=120.0) as client:
            # 1. train_test_split
            if not self.confirm("Proceed to train_test_split?"):
                return
            print("[1] Calling train_test_split...")
            url = self.base_url + "train_test_split"
            res = await client.post(url, json={"data": df_json, "test_size": 0.3})
            result = res.json()
            self.train_df = json_to_df(result['train_set'])
            self.test_df = json_to_df(result['test_set'])
            self.train_df.to_csv('./temp_files/http_train_set.csv', encoding='UTF-8')
            self.test_df.to_csv('./temp_files/http_test_set.csv', encoding='UTF-8')
            print("data sets saved")

            # 2. train_model
            if not self.confirm("Proceed to train_model?"):
                return
            print("[2] Calling train_model...")
            url = self.base_url + "train_model"
            res = await client.post(url, json={
                "train_data": df_to_json(self.train_df),
                "task": "classification",
                "mode": "stats",
                "target": "target"
            })
            self.modelid = res.json()["model_id"]
            print("model id: ", self.modelid)

            # 3. predict
            if not self.confirm("Proceed to predict?"):
                return
            print("[3] Calling predict...")
            url = self.base_url + "predict"
            res = await client.post(url, json={
                "test_data": df_to_json(self.test_df),
                "model_id": self.modelid
            })
            result = res.json()
            self.y_pred = result['prediction']
            print(self.y_pred)

            # 4. evaluate
            if not self.confirm("Proceed to evaluate?"):
                return
            print("[4] Calling evaluate...")
            url = self.base_url + "evaluate"
            res = await client.post(url, json={
                "test_data": df_to_json(self.test_df),
                "y_pred": self.y_pred,
                "model_id": self.modelid
            })
            result = res.json()
            eval = json_to_df(result['scores'])
            print("\nEvaluation result:")
            print(eval)

    def confirm(self, prompt):
        ans = input(f"{prompt} (y/n): ").strip().lower()
        return ans == 'y'

async def main():
    client = HTTPChainClient()
    try:
        await client.run_chain()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")

if __name__ == "__main__":
    asyncio.run(main()) 