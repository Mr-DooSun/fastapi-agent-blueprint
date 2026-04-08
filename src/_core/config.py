import warnings
from typing import Self

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

KNOWN_ENVS = ("local", "dev", "test", "stg", "prod")
STRICT_ENVS = frozenset({"stg", "prod"})

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
    env: str = Field("local", validation_alias=AliasChoices("ENV", "env"))

    # Taskiq task name prefix (e.g. "my-project.user.test")
    task_name_prefix: str = Field(
        default="my-project", validation_alias="TASK_NAME_PREFIX"
    )

    # ----------------------------------------------------------------
    # Admin Dashboard
    # ----------------------------------------------------------------
    admin_id: str = Field(default="admin", validation_alias="ADMIN_ID")
    admin_password: str = Field(default="admin", validation_alias="ADMIN_PASSWORD")
    admin_storage_secret: str = Field(
        default="change-me-in-production",
        validation_alias="ADMIN_STORAGE_SECRET",
    )

    # ----------------------------------------------------------------
    # Database
    # ----------------------------------------------------------------
    database_user: str = Field(default="postgres", validation_alias="DATABASE_USER")
    database_password: str = Field(
        default="postgres", validation_alias="DATABASE_PASSWORD"
    )
    database_host: str = Field(default="localhost", validation_alias="DATABASE_HOST")
    database_port: int = Field(default=5432, validation_alias="DATABASE_PORT")
    database_name: str = Field(default="postgres", validation_alias="DATABASE_NAME")

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
    # Messaging (AWS SQS)
    # ----------------------------------------------------------------
    aws_sqs_region: str | None = Field(default=None, validation_alias="AWS_SQS_REGION")
    aws_sqs_access_key: str = Field(validation_alias="AWS_SQS_ACCESS_KEY")
    aws_sqs_secret_key: str = Field(validation_alias="AWS_SQS_SECRET_KEY")
    aws_sqs_url: str = Field(validation_alias="AWS_SQS_URL")

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

        if errors:
            bullet_list = "\n  - ".join(errors)
            raise ValueError(
                f"Settings validation failed for env='{self.env}' "
                f"({len(errors)} error(s)):\n  - {bullet_list}"
            )

        return self

    @property
    def is_dev(self) -> bool:
        return self.env.lower() in {"dev", "local"}

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
    def allowed_hosts(self) -> list[str]:
        """Allowed host list for TrustedHostMiddleware."""
        if self.is_dev:
            return ["localhost", "127.0.0.1"]
        return ["api.example.com"]  # TODO: set production domain

    @property
    def allow_origins(self) -> list[str]:
        if self.is_dev:
            return ["*"]
        return ["https://example.com"]  # TODO: set production frontend domain


settings = Settings()
