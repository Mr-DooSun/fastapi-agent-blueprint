# -*- coding: utf-8 -*-

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # 환경 설정 (예: local, dev, stg, prod)
    env: str = Field(env="ENV")

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


settings = Settings()
