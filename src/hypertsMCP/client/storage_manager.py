from minio import Minio
from minio.error import S3Error
from typing import List, Optional
import pyarrow.parquet as pq
import pyarrow as pa
import os

class StorageManager:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = True
    ):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def _get_object_name(self, session_id: str, data_type: str, object_name: str) -> str:
        return f"{session_id}/{data_type}/{object_name}"

    def upload_file(
        self,
        session_id: str,
        data_type: str,
        object_name: str,
        file_path: str
    ) -> str:
        object_path = self._get_object_name(session_id, data_type, object_name)
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_path,
            file_path=file_path
        )
        return object_path
    
    def upload_obj(
        self,
        session_id: str,
        data_type: str,
        object_name: str,
        file_path: str
    ) -> str:
        object_path = self._get_object_name(session_id, data_type, object_name)
        table = pa.Table.from_pandas(df)
        parquet_buffer = BytesIO()
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)
        self.client.fput_object(
            bucket_name=self.bucket_name,
            object_name=object_path,
            file_path=file_path
        )
        return object_path

    def download_file(
        self,
        session_id: str,
        data_type: str,
        object_name: str,
        download_path: str
    ) -> str:
        object_path = self._get_object_path(session_id, data_type, object_name)
        self.client.fget_object(
            bucket_name=self.bucket_name,
            object_name=object_path,
            file_path=download_path
        )
        return download_path

    def list_files(
        self,
        session_id: str,
        data_type: Optional[str] = None
    ) -> List[str]:
        prefix = f"{session_id}/"
        if data_type:
            prefix += f"{data_type}/"

        objects = self.client.list_objects(
            bucket_name=self.bucket_name,
            prefix=prefix,
            recursive=True
        )
        return [obj.object_name for obj in objects]


storage = StorageManager(
    endpoint="http://192.168.252.36:30503",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="hyperts"
)

