# -*- coding: utf-8 -*-
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Optional

import aiohttp
from fastapi import HTTPException


def get_http_client_config(env: str):
    if env == "prod":
        return {
            "timeout": aiohttp.ClientTimeout(total=30, connect=10, sock_read=30),
            "connector": aiohttp.TCPConnector(
                limit=100,  # 전체 connection pool 크기
                limit_per_host=30,  # 호스트당 connection 수
                ttl_dns_cache=300,  # DNS 캐시 TTL (초)
                keepalive_timeout=30,  # Keep-alive 타임아웃
            ),
        }
    else:
        return {
            "timeout": aiohttp.ClientTimeout(total=10, connect=5, sock_read=10),
            "connector": aiohttp.TCPConnector(
                limit=50,
                limit_per_host=20,
                ttl_dns_cache=300,
            ),
        }


class HttpClient:
    def __init__(self, env: str) -> None:
        self.env = env
        self._config = get_http_client_config(env=env)
        self._client_session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        if self._client_session is None or self._client_session.closed:
            self._client_session = aiohttp.ClientSession(**self._config)
        return self._client_session

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        session = None

        try:
            session = await self._ensure_session()
            yield session
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=502, detail=f"External service error: {str(e)}"
            )
        except TimeoutError:
            raise HTTPException(status_code=504, detail="External service timeout")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"HTTP client error: {str(e)}")

    async def dispose(self) -> None:
        if self._client_session and not self._client_session.closed:
            await self._client_session.close()
            self._client_session = None
