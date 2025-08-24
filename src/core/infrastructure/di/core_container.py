# -*- coding: utf-8 -*-
from boto3 import client
from dependency_injector import containers, providers
from minio import Minio

from src.core.application.messaging.rabbitmq_publisher import RabbitMQPublisher
from src.core.domain.services.minio_service import MinioService
from src.core.domain.services.s3_service import S3Service
from src.core.infrastructure.database.database import Database
from src.core.infrastructure.messaging.rabbitmq_manager import RabbitMQManager


class CoreContainer(containers.DeclarativeContainer):
    config = providers.Configuration(strict=True)
    config.from_yaml("./config.yml")

    #########################################################
    # Database
    #########################################################

    database = providers.Singleton(
        Database,
        env=config.env,
        database_user=config.database.user,
        database_password=config.database.password,
        database_host=config.database.host,
        database_port=config.database.port,
        database_name=config.database.name,
    )

    #########################################################
    # Storage
    #########################################################

    minio_client = providers.Singleton(
        Minio,
        endpoint=config.minio.endpoint,
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        secure=False,  # HTTPS가 아닌 경우 False 설정
    )

    s3_client = providers.Singleton(
        client,
        service_name="s3",
        aws_access_key_id=config.s3.access_key,
        aws_secret_access_key=config.s3.secret_key,
        region_name=config.s3.region,
    )

    # Storage Services
    minio_service = providers.Factory(
        MinioService,
        minio_client=minio_client,
        bucket_name=config.minio.bucket_name,
    )

    s3_service = providers.Factory(
        S3Service,
        s3_client=s3_client,
        bucket_name=config.s3.bucket_name,
    )

    #########################################################
    # Messaging
    #########################################################

    rabbitmq_manager = providers.Singleton(
        RabbitMQManager,
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
    )

    rabbitmq_publisher = providers.Factory(
        RabbitMQPublisher, rabbitmq_manager=rabbitmq_manager
    )
