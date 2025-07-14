from minio import Minio
from minio.error import S3Error
from typing import List, Optional
import os
import uuid
import joblib

from dotenv import load_dotenv
load_dotenv()

# class StorageManager:
#     def __init__(
#         self,
#         endpoint: str,
#         access_key: str,
#         secret_key: str,
#         bucket_name: str,
#         secure: bool = True
#     ):
    
#         try:
#             self.client = Minio(
#                 endpoint=endpoint,
#                 access_key=access_key,
#                 secret_key=secret_key,
#                 secure=secure
#             )
#             self.bucket_name = bucket_name
#             self._ensure_bucket_exists()
#         except Exception as e:
#             raise ConnectionError(f"Failed to initialize MinIO client: {e}")

#     def _ensure_bucket_exists(self):
#         try:
#             if not self.client.bucket_exists(self.bucket_name):
#                 self.client.make_bucket(self.bucket_name)
#         except S3Error as e:
#             raise ConnectionError(f"Failed to access or create bucket '{self.bucket_name}': {e}")

#     def _get_object_path(self, session_id: str, data_type: str, object_name: str) -> str:
#         return f"{session_id}/{data_type}/{object_name}"

#     def upload_file(
#         self,
#         session_id: str,
#         data_type: str,
#         object_name: str,
#         file_path: str
#     ) -> str:
#         object_path = self._get_object_path(session_id, data_type, object_name)
#         self.client.fput_object(
#             bucket_name=self.bucket_name,
#             object_name=object_path,
#             file_path=file_path
#         )
#         return object_path

#     def download_file(
#         self,
#         session_id: str,
#         data_type: str,
#         object_name: str,
#         download_path: str
#     ) -> str:
#         object_path = self._get_object_path(session_id, data_type, object_name)
#         self.client.fget_object(
#             bucket_name=self.bucket_name,
#             object_name=object_path,
#             file_path=download_path
#         )
#         return download_path

#     def list_files(
#         self,
#         session_id: str,
#         data_type: Optional[str] = None
#     ) -> List[str]:
#         prefix = f"{session_id}/"
#         if data_type:
#             prefix += f"{data_type}/"

#         objects = self.client.list_objects(
#             bucket_name=self.bucket_name,
#             prefix=prefix,
#             recursive=True
#         )
#         return [obj.object_name for obj in objects]

    # def delete_file(
    #     self,
    #     session_id: str,
    #     data_type: str,
    #     object_name: str
    # ) -> None:
    #     """删除指定文件"""
    #     object_path = self._get_object_path(session_id, data_type, object_name)
    #     self.client.remove_object(
    #         bucket_name=self.bucket_name,
    #         object_name=object_path
    #     )

    # def delete_session_files(self, session_id: str) -> None:
    #     """删除整个 session 的所有数据（谨慎操作！）"""
    #     objects = self.list_files(session_id)
    #     for obj_path in objects:
    #         self.client.remove_object(
    #             bucket_name=self.bucket_name,
    #             object_name=obj_path
    #         )

# def create_storage_manager() -> StorageManager:
#     """
#     a method that creates StorageManager instance using environment variables or defaults
#     """
#     endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
#     access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
#     secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")
#     bucket_name = os.getenv("MINIO_BUCKET_NAME", "hyperts")
#     secure = os.getenv("MINIO_SECURE", "false").lower() == "true"
#     print("\n endpoint: ", endpoint)

#     return StorageManager(
#         endpoint=endpoint,
#         access_key=access_key,
#         secret_key=secret_key,
#         bucket_name=bucket_name,
#         secure=secure
#     )

# # initialize a storage manager
# try:
#     storage = create_storage_manager()
# except ConnectionError as e:
#     print(f"Storage manager initialization failed: {e}")
#     storage = None


