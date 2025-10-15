# -*- coding: utf-8 -*-
from abc import ABC
from typing import Any, Dict, Optional

from src._core.infrastructure.http.http_client import HttpClient


class BaseHttpRepository(ABC):
    def __init__(self, http_client: HttpClient, base_url: str) -> None:
        self.http_client = http_client
        self.base_url = base_url

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.get(
                f"{self.base_url}{endpoint}", params=params, headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.post(
                f"{self.base_url}{endpoint}", json=json, headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.put(
                f"{self.base_url}{endpoint}", json=json, headers=headers
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None
    ) -> bool:
        async with self.http_client.session() as session:
            async with session.delete(
                f"{self.base_url}{endpoint}", headers=headers
            ) as response:
                response.raise_for_status()
                return True
