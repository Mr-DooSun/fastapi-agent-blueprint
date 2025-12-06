from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ----------------------------------------------------------------
    # 공통 설정
    # ----------------------------------------------------------------
    # 환경 설정 (예: local, dev, stg, prod)
    env: str = Field("local", validation_alias=AliasChoices("ENV", "env"))

    # ----------------------------------------------------------------
    # Database
    # ----------------------------------------------------------------
    database_user: str = Field(default="postgres", validation_alias="DATABASE_USER")
    database_password: str = Field(default="postgres", validation_alias="DATABASE_PASSWORD")
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
    minio_access_key: str | None = Field(default=None, validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str | None = Field(default=None, validation_alias="MINIO_SECRET_KEY")
    minio_bucket_name: str | None = Field(default=None, validation_alias="MINIO_BUCKET_NAME")

    # ----------------------------------------------------------------
    # Messaging (AWS SQS)
    # ----------------------------------------------------------------
    aws_sqs_region: str | None = Field(default=None, validation_alias="AWS_SQS_REGION")
    aws_sqs_access_key: str | None = Field(default=None, validation_alias="AWS_SQS_ACCESS_KEY")
    aws_sqs_secret_key: str | None = Field(default=None, validation_alias="AWS_SQS_SECRET_KEY")
    aws_sqs_queue: str | None = Field(default=None, validation_alias="AWS_SQS_QUEUE")

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
        """TrustedHostMiddleware 용 호스트 목록"""
        if self.is_dev:
            return ["localhost", "127.0.0.1"]
        return ["api.example.com"] # TODO: 실제 운영 도메인 입력 필요

    @property
    def allow_origins(self) -> list[str]:
        if self.is_dev:
            return ["*"]
        return ["https://example.com"] # TODO: 실제 프론트엔드 도메인 입력 필요


settings = Settings()
