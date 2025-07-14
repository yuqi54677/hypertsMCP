from minio import Minio
from minio.error import S3Error
from typing import List, Optional
import os
# import os
import uuid
import joblib


class StorageManager:
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        secure: bool = True
    ):
        """
        初始化 MinIO 客户端和存储桶
        :param bucket_name: 统一的存储桶名称
        """
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure
        )
        self.bucket_name = bucket_name
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        """检查存储桶是否存在，不存在则创建"""
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    def _get_object_path(self, session_id: str, data_type: str, object_name: str) -> str:
        """生成带前缀的对象路径（如 'session123/model/model.pkl'）"""
        return f"{session_id}/{data_type}/{object_name}"

    def upload_file(
        self,
        session_id: str,
        data_type: str,
        object_name: str,
        file_path: str
    ) -> str:
        """
        上传文件到指定 session 和数据类型目录
        :return: 存储的完整路径（含前缀）
        """
        object_path = self._get_object_path(session_id, data_type, object_name)
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
        """下载文件到本地指定路径"""
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
        """
        列出 session 下的所有文件（可限定数据类型）
        :return: 对象的完整路径列表
        """
        prefix = f"{session_id}/"
        if data_type:
            prefix += f"{data_type}/"

        objects = self.client.list_objects(
            bucket_name=self.bucket_name,
            prefix=prefix,
            recursive=True
        )
        return [obj.object_name for obj in objects]

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

storage = StorageManager(
    endpoint="http://192.168.252.36:30503",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="hyperts"
)


class ModelStore:
    base_dir = "./models"

    @classmethod
    def save(cls, model) -> str:
        os.makedirs(cls.base_dir, exist_ok=True)
        model_id = str(uuid.uuid4())
        path = os.path.join(cls.base_dir, f"{model_id}.pkl")
        joblib.dump(model, path)
        return model_id

    @classmethod
    def load(cls, model_id: str):
        path = os.path.join(cls.base_dir, f"{model_id}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model {model_id} not found")
        return joblib.load(path)