import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp
from fastapi import HTTPException


def get_http_client_config(env: str):
    if env == "prod":
        return {
            "timeout": aiohttp.ClientTimeout(total=30, connect=10, sock_read=30),
            "connector_kwargs": {
                "limit": 100,
                "limit_per_host": 30,
                "ttl_dns_cache": 300,
                "keepalive_timeout": 30,
            },
        }
    else:
        return {
            "timeout": aiohttp.ClientTimeout(total=10, connect=5, sock_read=10),
            "connector_kwargs": {
                "limit": 50,
                "limit_per_host": 20,
                "ttl_dns_cache": 300,
            },
        }


class HttpClient:
    def __init__(self, env: str) -> None:
        self.env = env
        self._config = get_http_client_config(env=env)
        self._client_session: aiohttp.ClientSession | None = None
        self._session_loop: asyncio.AbstractEventLoop | None = None

    async def _ensure_session(self) -> aiohttp.ClientSession:
        # 현재 실행 중인 루프 확인
        try:
            current_loop = asyncio.get_running_loop()
            if self._client_session and self._session_loop != current_loop:
                # 루프가 변경되었거나 닫힌 경우 세션 초기화
                self._client_session = None
                self._session_loop = None
        except RuntimeError:
            # 루프가 없는 경우 (동기 컨텍스트 등) - 여기서는 무시하거나 새로 생성
            pass

        if self._client_session is None or self._client_session.closed:
            connector = aiohttp.TCPConnector(**self._config["connector_kwargs"])
            self._client_session = aiohttp.ClientSession(
                timeout=self._config["timeout"],
                connector=connector,
            )
            try:
                self._session_loop = asyncio.get_running_loop()
            except RuntimeError:
                self._session_loop = None
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
