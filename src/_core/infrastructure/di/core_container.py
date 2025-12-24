from dependency_injector import containers, providers

from src._core.config import settings
from src._core.infrastructure.database.config import DatabaseConfig
from src._core.infrastructure.database.database import Database
from src._core.infrastructure.http.http_client import HttpClient
from src._core.infrastructure.storage.object_storage import ObjectStorage
from src._core.infrastructure.storage.object_storage_client import ObjectStorageClient


class CoreContainer(containers.DeclarativeContainer):
    #########################################################
    # Database
    #########################################################

    db_config = providers.Factory(
        DatabaseConfig.from_env,
        env=settings.env,
    )

    database = providers.Singleton(
        Database,
        database_user=settings.database_user,
        database_password=settings.database_password,
        database_host=settings.database_host,
        database_port=settings.database_port,
        database_name=settings.database_name,
        config=db_config,
    )

    #########################################################
    # HTTP Client
    #########################################################

    http_client = providers.Singleton(
        HttpClient,
        env=settings.env,
    )

    #########################################################
    # Storage
    #########################################################

    # MinIO용 설정 (필요시 교체 사용)
    # minio_client = providers.Singleton(
    #     ObjectStorageClient,
    #     access_key=settings.minio_access_key,
    #     secret_access_key=settings.minio_secret_key,
    #     endpoint_url=settings.minio_endpoint_url,
    # )

    # AWS S3용 설정
    s3_client = providers.Singleton(
        ObjectStorageClient,
        access_key=settings.s3_access_key,
        secret_access_key=settings.s3_secret_key,
        region_name=settings.s3_region,
    )

    s3_storage = providers.Factory(
        ObjectStorage,
        storage_client=s3_client,
        bucket_name=settings.s3_bucket_name,
    )
