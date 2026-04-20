import warnings
from typing import Self

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

KNOWN_ENVS = ("quickstart", "local", "dev", "stg", "prod")
KNOWN_ENGINES = ("postgresql", "mysql", "sqlite")
KNOWN_BROKER_TYPES = ("sqs", "rabbitmq", "inmemory")
KNOWN_EMBEDDING_PROVIDERS = (
    "openai",
    "bedrock",
    "google",
    "ollama",
    "sentence-transformers",
)
KNOWN_STORAGE_TYPES = ("s3", "minio")
KNOWN_LLM_PROVIDERS = ("openai", "anthropic", "bedrock")
STRICT_ENVS = frozenset({"stg", "prod"})

_OPENAI_DIMENSIONS: dict[str, int] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}
_BEDROCK_DIMENSIONS: dict[str, int] = {
    "amazon.titan-embed-text-v2:0": 1024,
    "amazon.titan-embed-text-v1": 1536,
}
_GOOGLE_DIMENSIONS: dict[str, int] = {
    "gemini-embedding-001": 768,
    "text-embedding-004": 768,
    "text-multilingual-embedding-002": 768,
}
_LOCAL_DIMENSIONS: dict[str, int] = {
    "nomic-embed-text": 768,
    "all-MiniLM-L6-v2": 384,
    "all-mpnet-base-v2": 768,
}

_UNSAFE_DEFAULTS: dict[str, str] = {
    "admin_password": "admin",  # noqa: S105
    "admin_storage_secret": "change-me-in-production",  # noqa: S105
    "database_password": "postgres",  # noqa: S105
    "database_host": "localhost",
}

_WARN_DEFAULTS: dict[str, str] = {
    "task_name_prefix": "my-project",
}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ----------------------------------------------------------------
    # General
    # ----------------------------------------------------------------
    # Environment (e.g. local, dev, stg, prod)
    env: str = Field(default="local", validation_alias=AliasChoices("ENV", "env"))

    # Taskiq task name prefix (e.g. "my-project.user.test")
    task_name_prefix: str = Field(
        default="my-project", validation_alias="TASK_NAME_PREFIX"
    )

    # ----------------------------------------------------------------
    # Admin Dashboard
    #
    # Defaults here are intentionally unsafe ("admin"/"admin") so that
    # `make quickstart` runs with no configuration. They are blocked in
    # stg/prod by the `_UNSAFE_DEFAULTS` check below; callers in real
    # deployments must override them via env vars.
    # ----------------------------------------------------------------
    admin_id: str = Field(default="admin", validation_alias="ADMIN_ID")
    admin_password: str = Field(default="admin", validation_alias="ADMIN_PASSWORD")
    admin_storage_secret: str = Field(
        default="change-me-in-production", validation_alias="ADMIN_STORAGE_SECRET"
    )

    # ----------------------------------------------------------------
    # Database
    #
    # Defaults target the zero-config SQLite path used by `make quickstart`.
    # For non-sqlite engines, the user/password/host/port/name fields must
    # all be supplied via env vars. stg/prod additionally reject the
    # unsafe-password and unsafe-host defaults via `_UNSAFE_DEFAULTS`.
    # ----------------------------------------------------------------
    database_engine: str = Field(default="sqlite", validation_alias="DATABASE_ENGINE")
    database_user: str = Field(default="postgres", validation_alias="DATABASE_USER")
    database_password: str = Field(
        default="postgres", validation_alias="DATABASE_PASSWORD"
    )
    database_host: str = Field(default="localhost", validation_alias="DATABASE_HOST")
    database_port: int = Field(default=5432, validation_alias="DATABASE_PORT")
    database_name: str = Field(
        default="./quickstart.db", validation_alias="DATABASE_NAME"
    )
    database_pool_size: int | None = Field(
        default=None, validation_alias="DATABASE_POOL_SIZE"
    )
    database_max_overflow: int | None = Field(
        default=None, validation_alias="DATABASE_MAX_OVERFLOW"
    )
    database_pool_recycle: int | None = Field(
        default=None, validation_alias="DATABASE_POOL_RECYCLE"
    )
    database_echo: bool | None = Field(default=None, validation_alias="DATABASE_ECHO")

    # ----------------------------------------------------------------
    # Storage (AWS S3)
    # ----------------------------------------------------------------
    s3_access_key: str | None = Field(default=None, validation_alias="S3_ACCESS_KEY")
    s3_secret_key: str | None = Field(default=None, validation_alias="S3_SECRET_KEY")
    s3_region: str | None = Field(default=None, validation_alias="S3_REGION")
    s3_bucket_name: str | None = Field(default=None, validation_alias="S3_BUCKET_NAME")

    # ----------------------------------------------------------------
    # Storage (MinIO)
    # ----------------------------------------------------------------
    minio_host: str | None = Field(default=None, validation_alias="MINIO_HOST")
    minio_port: int | None = Field(default=None, validation_alias="MINIO_PORT")
    minio_access_key: str | None = Field(
        default=None, validation_alias="MINIO_ACCESS_KEY"
    )
    minio_secret_key: str | None = Field(
        default=None, validation_alias="MINIO_SECRET_KEY"
    )
    minio_bucket_name: str | None = Field(
        default=None, validation_alias="MINIO_BUCKET_NAME"
    )

    # ----------------------------------------------------------------
    # Storage Type Selector (s3 / minio)
    # ----------------------------------------------------------------
    storage_type: str | None = Field(default=None, validation_alias="STORAGE_TYPE")

    # ----------------------------------------------------------------
    # DynamoDB (Optional)
    # ----------------------------------------------------------------
    dynamodb_region: str | None = Field(
        default=None, validation_alias="DYNAMODB_REGION"
    )
    dynamodb_access_key: str | None = Field(
        default=None, validation_alias="DYNAMODB_ACCESS_KEY"
    )
    dynamodb_secret_key: str | None = Field(
        default=None, validation_alias="DYNAMODB_SECRET_KEY"
    )
    dynamodb_endpoint_url: str | None = Field(
        default=None, validation_alias="DYNAMODB_ENDPOINT_URL"
    )

    # ----------------------------------------------------------------
    # S3 Vectors (Optional)
    # ----------------------------------------------------------------
    s3vectors_region: str | None = Field(
        default=None, validation_alias="S3VECTORS_REGION"
    )
    s3vectors_access_key: str | None = Field(
        default=None, validation_alias="S3VECTORS_ACCESS_KEY"
    )
    s3vectors_secret_key: str | None = Field(
        default=None, validation_alias="S3VECTORS_SECRET_KEY"
    )
    s3vectors_bucket_name: str | None = Field(
        default=None, validation_alias="S3VECTORS_BUCKET_NAME"
    )

    # ----------------------------------------------------------------
    # Message Broker
    # ----------------------------------------------------------------
    broker_type: str | None = Field(default=None, validation_alias="BROKER_TYPE")

    # ----------------------------------------------------------------
    # Messaging (AWS SQS) — required when BROKER_TYPE=sqs
    # ----------------------------------------------------------------
    aws_sqs_region: str | None = Field(default=None, validation_alias="AWS_SQS_REGION")
    aws_sqs_access_key: str | None = Field(
        default=None, validation_alias="AWS_SQS_ACCESS_KEY"
    )
    aws_sqs_secret_key: str | None = Field(
        default=None, validation_alias="AWS_SQS_SECRET_KEY"
    )
    aws_sqs_url: str | None = Field(default=None, validation_alias="AWS_SQS_URL")

    # ----------------------------------------------------------------
    # Messaging (RabbitMQ) — required when BROKER_TYPE=rabbitmq
    # ----------------------------------------------------------------
    rabbitmq_url: str | None = Field(default=None, validation_alias="RABBITMQ_URL")

    # ----------------------------------------------------------------
    # Embedding (Optional)
    # ----------------------------------------------------------------
    embedding_provider: str | None = Field(
        default=None, validation_alias="EMBEDDING_PROVIDER"
    )
    embedding_model: str | None = Field(
        default=None, validation_alias="EMBEDDING_MODEL"
    )

    # OpenAI-specific (required when EMBEDDING_PROVIDER=openai)
    embedding_openai_api_key: str | None = Field(
        default=None, validation_alias="EMBEDDING_OPENAI_API_KEY"
    )

    # Bedrock-specific (required when EMBEDDING_PROVIDER=bedrock)
    embedding_bedrock_access_key: str | None = Field(
        default=None, validation_alias="EMBEDDING_BEDROCK_ACCESS_KEY"
    )
    embedding_bedrock_secret_key: str | None = Field(
        default=None, validation_alias="EMBEDDING_BEDROCK_SECRET_KEY"
    )
    embedding_bedrock_region: str | None = Field(
        default=None, validation_alias="EMBEDDING_BEDROCK_REGION"
    )

    # ----------------------------------------------------------------
    # LLM (Optional — required when using PydanticAI agents)
    # ----------------------------------------------------------------
    llm_provider: str | None = Field(default=None, validation_alias="LLM_PROVIDER")
    llm_model: str | None = Field(default=None, validation_alias="LLM_MODEL")
    llm_api_key: str | None = Field(default=None, validation_alias="LLM_API_KEY")

    # Bedrock-specific (required when LLM_PROVIDER=bedrock)
    llm_bedrock_access_key: str | None = Field(
        default=None, validation_alias="LLM_BEDROCK_ACCESS_KEY"
    )
    llm_bedrock_secret_key: str | None = Field(
        default=None, validation_alias="LLM_BEDROCK_SECRET_KEY"
    )
    llm_bedrock_region: str | None = Field(
        default=None, validation_alias="LLM_BEDROCK_REGION"
    )

    # ----------------------------------------------------------------
    # Network Policy
    # ----------------------------------------------------------------
    allowed_hosts: list[str] = Field(
        default=["localhost", "127.0.0.1"],
        validation_alias="ALLOWED_HOSTS",
    )
    allow_origins: list[str] = Field(
        default=["*"],
        validation_alias="ALLOW_ORIGINS",
    )

    # ----------------------------------------------------------------

    @model_validator(mode="after")
    def _validate_environment_safety(self) -> Self:
        errors: list[str] = []
        env = self.env.lower()

        if env not in KNOWN_ENVS:
            errors.append(
                f"[env] Unknown environment '{self.env}'. "
                f"Expected one of: {', '.join(KNOWN_ENVS)}"
            )

        engine = self.database_engine.lower()
        if engine not in KNOWN_ENGINES:
            errors.append(
                f"[database_engine] Unknown engine '{self.database_engine}'. "
                f"Expected one of: {', '.join(KNOWN_ENGINES)}"
            )

        if env in STRICT_ENVS:
            for field_name, unsafe_value in _UNSAFE_DEFAULTS.items():
                if getattr(self, field_name) == unsafe_value:
                    errors.append(
                        f"[{field_name}] Using unsafe default "
                        f"'{unsafe_value}' in '{self.env}' environment"
                    )

            for field_name, default_value in _WARN_DEFAULTS.items():
                if getattr(self, field_name) == default_value:
                    warnings.warn(
                        f"Settings: [{field_name}] still uses default "
                        f"'{default_value}' in '{self.env}' environment",
                        stacklevel=2,
                    )

        s3_fields = {
            "s3_access_key": self.s3_access_key,
            "s3_secret_key": self.s3_secret_key,
            "s3_region": self.s3_region,
            "s3_bucket_name": self.s3_bucket_name,
        }
        s3_set = {k for k, v in s3_fields.items() if v is not None}
        if s3_set and s3_set != set(s3_fields):
            missing = sorted(set(s3_fields) - s3_set)
            errors.append(
                f"[S3] Partial configuration: {', '.join(sorted(s3_set))} "
                f"set but {', '.join(missing)} missing"
            )

        minio_fields = {
            "minio_host": self.minio_host,
            "minio_port": self.minio_port,
            "minio_access_key": self.minio_access_key,
            "minio_secret_key": self.minio_secret_key,
            "minio_bucket_name": self.minio_bucket_name,
        }
        minio_set = {k for k, v in minio_fields.items() if v is not None}
        if minio_set and minio_set != set(minio_fields):
            missing = sorted(set(minio_fields) - minio_set)
            errors.append(
                f"[MinIO] Partial configuration: {', '.join(sorted(minio_set))} "
                f"set but {', '.join(missing)} missing"
            )

        storage = (self.storage_type or "").lower().strip()
        if storage and storage not in KNOWN_STORAGE_TYPES:
            errors.append(
                f"[storage_type] Unknown storage type '{self.storage_type}'. "
                f"Expected one of: {', '.join(KNOWN_STORAGE_TYPES)}"
            )
        if storage == "s3" and s3_set != set(s3_fields):
            missing = sorted(set(s3_fields) - s3_set)
            errors.append(
                f"[Storage] STORAGE_TYPE=s3 requires: {', '.join(missing)} missing"
            )
        if storage == "minio" and minio_set != set(minio_fields):
            missing = sorted(set(minio_fields) - minio_set)
            errors.append(
                f"[Storage] STORAGE_TYPE=minio requires: {', '.join(missing)} missing"
            )

        dynamodb_fields = {
            "dynamodb_region": self.dynamodb_region,
            "dynamodb_access_key": self.dynamodb_access_key,
            "dynamodb_secret_key": self.dynamodb_secret_key,
        }
        dynamodb_set = {k for k, v in dynamodb_fields.items() if v is not None}
        if dynamodb_set and dynamodb_set != set(dynamodb_fields):
            missing = sorted(set(dynamodb_fields) - dynamodb_set)
            errors.append(
                f"[DynamoDB] Partial configuration: "
                f"{', '.join(sorted(dynamodb_set))} "
                f"set but {', '.join(missing)} missing"
            )

        s3vectors_fields = {
            "s3vectors_region": self.s3vectors_region,
            "s3vectors_access_key": self.s3vectors_access_key,
            "s3vectors_secret_key": self.s3vectors_secret_key,
            "s3vectors_bucket_name": self.s3vectors_bucket_name,
        }
        s3vectors_set = {k for k, v in s3vectors_fields.items() if v is not None}
        if s3vectors_set and s3vectors_set != set(s3vectors_fields):
            missing = sorted(set(s3vectors_fields) - s3vectors_set)
            errors.append(
                f"[S3Vectors] Partial configuration: "
                f"{', '.join(sorted(s3vectors_set))} "
                f"set but {', '.join(missing)} missing"
            )

        broker = (self.broker_type or "").lower().strip()
        if env in STRICT_ENVS and not broker:
            errors.append(
                f"[broker_type] BROKER_TYPE is required in '{self.env}' environment"
            )
        if broker and broker not in KNOWN_BROKER_TYPES:
            errors.append(
                f"[broker_type] Unknown broker type '{self.broker_type}'. "
                f"Expected one of: {', '.join(KNOWN_BROKER_TYPES)}"
            )

        if broker == "sqs":
            sqs_fields = {
                "aws_sqs_access_key": self.aws_sqs_access_key,
                "aws_sqs_secret_key": self.aws_sqs_secret_key,
                "aws_sqs_url": self.aws_sqs_url,
            }
            sqs_set = {k for k, v in sqs_fields.items() if v is not None}
            if sqs_set != set(sqs_fields):
                missing = sorted(set(sqs_fields) - sqs_set)
                errors.append(
                    f"[SQS] BROKER_TYPE=sqs requires: {', '.join(missing)} missing"
                )

        if broker == "rabbitmq" and not self.rabbitmq_url:
            errors.append(
                "[RabbitMQ] BROKER_TYPE=rabbitmq requires: rabbitmq_url missing"
            )

        llm = (self.llm_provider or "").lower().strip()
        if llm and llm not in KNOWN_LLM_PROVIDERS:
            errors.append(
                f"[llm_provider] Unknown LLM provider '{self.llm_provider}'. "
                f"Expected one of: {', '.join(KNOWN_LLM_PROVIDERS)}"
            )

        if llm in ("openai", "anthropic") and not self.llm_api_key:
            errors.append(f"[LLM] LLM_PROVIDER={llm} requires: llm_api_key missing")

        if llm == "bedrock":
            llm_bedrock_fields = {
                "llm_bedrock_access_key": self.llm_bedrock_access_key,
                "llm_bedrock_secret_key": self.llm_bedrock_secret_key,
                "llm_bedrock_region": self.llm_bedrock_region,
            }
            llm_bedrock_set = {
                k for k, v in llm_bedrock_fields.items() if v is not None
            }
            if llm_bedrock_set != set(llm_bedrock_fields):
                missing = sorted(set(llm_bedrock_fields) - llm_bedrock_set)
                errors.append(
                    f"[LLM/Bedrock] LLM_PROVIDER=bedrock requires: "
                    f"{', '.join(missing)} missing"
                )

        embedding = (self.embedding_provider or "").lower().strip()
        if embedding and embedding not in KNOWN_EMBEDDING_PROVIDERS:
            errors.append(
                f"[embedding_provider] Unknown embedding provider "
                f"'{self.embedding_provider}'. "
                f"Expected one of: {', '.join(KNOWN_EMBEDDING_PROVIDERS)}"
            )

        if embedding == "openai":
            if not self.embedding_openai_api_key:
                errors.append(
                    "[Embedding/OpenAI] EMBEDDING_PROVIDER=openai requires: "
                    "embedding_openai_api_key missing"
                )

        if embedding == "bedrock":
            bedrock_fields = {
                "embedding_bedrock_access_key": self.embedding_bedrock_access_key,
                "embedding_bedrock_secret_key": self.embedding_bedrock_secret_key,
                "embedding_bedrock_region": self.embedding_bedrock_region,
            }
            bedrock_set = {k for k, v in bedrock_fields.items() if v is not None}
            if bedrock_set != set(bedrock_fields):
                missing = sorted(set(bedrock_fields) - bedrock_set)
                errors.append(
                    f"[Embedding/Bedrock] EMBEDDING_PROVIDER=bedrock requires: "
                    f"{', '.join(missing)} missing"
                )

        if errors:
            bullet_list = "\n  - ".join(errors)
            raise ValueError(
                f"Settings validation failed for env='{self.env}' "
                f"({len(errors)} error(s)):\n  - {bullet_list}"
            )

        return self

    @property
    def is_dev(self) -> bool:
        return self.env.lower() in {"quickstart", "dev", "local"}

    @property
    def docs_url(self) -> str | None:
        return "/docs-swagger" if self.is_dev else None

    @property
    def redoc_url(self) -> str | None:
        return "/docs-redoc" if self.is_dev else None

    @property
    def openapi_url(self) -> str | None:
        return "/openapi.json" if self.is_dev else None

    @property
    def minio_endpoint_url(self) -> str | None:
        if self.minio_host and self.minio_port:
            return f"{self.minio_host}:{self.minio_port}"
        return None

    @property
    def storage_access_key(self) -> str | None:
        st = (self.storage_type or "").lower()
        if st == "s3":
            return self.s3_access_key
        if st == "minio":
            return self.minio_access_key
        return None

    @property
    def storage_secret_key(self) -> str | None:
        st = (self.storage_type or "").lower()
        if st == "s3":
            return self.s3_secret_key
        if st == "minio":
            return self.minio_secret_key
        return None

    @property
    def storage_region(self) -> str | None:
        st = (self.storage_type or "").lower()
        if st == "s3":
            return self.s3_region
        if st == "minio":
            return "us-east-1"
        return None

    @property
    def storage_endpoint_url(self) -> str | None:
        st = (self.storage_type or "").lower()
        if st == "minio":
            return self.minio_endpoint_url
        return None

    @property
    def storage_bucket_name(self) -> str | None:
        st = (self.storage_type or "").lower()
        if st == "s3":
            return self.s3_bucket_name
        if st == "minio":
            return self.minio_bucket_name
        return None

    @property
    def embedding_dimension(self) -> int:
        """Derive embedding vector dimension from provider and model.

        Not user-configurable — determined by the selected model.
        Used as the single source of truth for ``S3VectorModelMeta.dimension``.
        """
        provider = (self.embedding_provider or "openai").lower()
        model = self.embedding_model
        if provider == "bedrock":
            return _BEDROCK_DIMENSIONS.get(
                model or "amazon.titan-embed-text-v2:0", 1024
            )
        if provider == "google":
            return _GOOGLE_DIMENSIONS.get(model or "gemini-embedding-001", 768)
        if provider in ("ollama", "sentence-transformers"):
            return _LOCAL_DIMENSIONS.get(model or "nomic-embed-text", 768)
        return _OPENAI_DIMENSIONS.get(model or "text-embedding-3-small", 1536)

    @property
    def embedding_model_name(self) -> str | None:
        """PydanticAI-compatible embedding model string.

        e.g. ``'openai:text-embedding-3-small'``, ``'bedrock:amazon.titan-embed-text-v2:0'``.
        Returns ``None`` when embedding is not configured.
        """
        provider = (self.embedding_provider or "").lower().strip()
        model = self.embedding_model
        if not provider or not model:
            return None
        return f"{provider}:{model}"

    @property
    def llm_model_name(self) -> str | None:
        """PydanticAI-compatible model string (e.g. ``'openai:gpt-4o'``).

        Returns ``None`` when LLM is not configured.
        """
        provider = (self.llm_provider or "").lower().strip()
        model = self.llm_model
        if not provider or not model:
            return None
        return f"{provider}:{model}"


settings = Settings()
