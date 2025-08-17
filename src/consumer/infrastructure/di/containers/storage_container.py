# -*- coding: utf-8 -*-

from dependency_injector import containers, providers

from src.core.domain.services.minio_service import MinioService
from src.core.domain.services.s3_service import S3Service


class StorageContainer(containers.DeclarativeContainer):
    core_container = providers.DependenciesContainer()

    minio_service = providers.Factory(
        MinioService,
        minio_client=core_container.minio_client,
        bucket_name=core_container.config.provided.minio.bucket_name,
    )

    s3_service = providers.Factory(
        S3Service,
        s3_client=core_container.s3_client,
        bucket_name=core_container.config.provided.s3.bucket_name,
    )
