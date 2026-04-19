from dependency_injector import containers, providers
from taskiq import InMemoryBroker

from src._core.config import settings
from src._core.domain.value_objects.embedding_config import EmbeddingConfig
from src._core.domain.value_objects.llm_config import LLMConfig
from src._core.infrastructure.embedding.pydantic_ai_embedding_adapter import (
    PydanticAIEmbeddingAdapter,
)
from src._core.infrastructure.http.http_client import HttpClient
from src._core.infrastructure.llm.model_factory import build_llm_model
from src._core.infrastructure.persistence.nosql.dynamodb.dynamodb_client import (
    DynamoDBClient,
)
from src._core.infrastructure.persistence.rdb.config import DatabaseConfig
from src._core.infrastructure.persistence.rdb.database import Database
from src._core.infrastructure.storage.object_storage import ObjectStorage
from src._core.infrastructure.storage.object_storage_client import ObjectStorageClient
from src._core.infrastructure.taskiq.broker import (
    create_rabbitmq_broker,
    create_sqs_broker,
)
from src._core.infrastructure.taskiq.manager import TaskiqManager
from src._core.infrastructure.vectors.s3.client import S3VectorClient


class CoreContainer(containers.DeclarativeContainer):
    #########################################################
    # Database
    #########################################################

    db_config = providers.Factory(
        DatabaseConfig.from_env,
        env=settings.env,
        engine=settings.database_engine,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_recycle=settings.database_pool_recycle,
        echo=settings.database_echo,
    )

    database = providers.Singleton(
        Database,
        database_engine=settings.database_engine,
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

    storage_client = providers.Singleton(
        ObjectStorageClient,
        access_key=settings.storage_access_key,
        secret_access_key=settings.storage_secret_key,
        region_name=settings.storage_region,
        endpoint_url=settings.storage_endpoint_url,
    )

    storage = providers.Factory(
        ObjectStorage,
        storage_client=storage_client,
        bucket_name=settings.storage_bucket_name,
    )

    #########################################################
    # DynamoDB
    #########################################################

    dynamodb_client = providers.Singleton(
        DynamoDBClient,
        access_key=settings.dynamodb_access_key,
        secret_access_key=settings.dynamodb_secret_key,
        region_name=settings.dynamodb_region,
        endpoint_url=settings.dynamodb_endpoint_url,
    )

    #########################################################
    # S3 Vectors
    #########################################################

    s3vector_client = providers.Singleton(
        S3VectorClient,
        access_key=settings.s3vectors_access_key,
        secret_access_key=settings.s3vectors_secret_key,
        region_name=settings.s3vectors_region,
    )

    #########################################################
    # Message Queue (Taskiq)
    #########################################################

    broker = providers.Selector(
        lambda: (settings.broker_type or "inmemory").lower().strip(),
        sqs=providers.Singleton(
            create_sqs_broker,
            queue_url=settings.aws_sqs_url,
            aws_region=settings.aws_sqs_region,
            aws_access_key_id=settings.aws_sqs_access_key,
            aws_secret_access_key=settings.aws_sqs_secret_key,
        ),
        rabbitmq=providers.Singleton(
            create_rabbitmq_broker,
            url=settings.rabbitmq_url,
        ),
        inmemory=providers.Singleton(InMemoryBroker),
    )

    taskiq_manager = providers.Singleton(
        TaskiqManager,
        broker=broker,
    )

    #########################################################
    # LLM Config (Optional — for PydanticAI agents)
    #########################################################

    llm_config = providers.Singleton(
        LLMConfig,
        model_name=settings.llm_model_name or "",
        api_key=settings.llm_api_key,
        aws_access_key_id=settings.llm_bedrock_access_key,
        aws_secret_access_key=settings.llm_bedrock_secret_key,
        aws_region=settings.llm_bedrock_region,
    )

    llm_model = providers.Singleton(
        build_llm_model,
        llm_config=llm_config,
    )

    #########################################################
    # Embedding Config + Client (Optional — for PydanticAI)
    #########################################################

    embedding_config = providers.Singleton(
        EmbeddingConfig,
        model_name=settings.embedding_model_name or "",
        dimension=settings.embedding_dimension,
        api_key=settings.embedding_openai_api_key,
        aws_access_key_id=settings.embedding_bedrock_access_key,
        aws_secret_access_key=settings.embedding_bedrock_secret_key,
        aws_region=settings.embedding_bedrock_region,
    )

    embedding_client = providers.Singleton(
        PydanticAIEmbeddingAdapter,
        embedding_config=embedding_config,
    )
