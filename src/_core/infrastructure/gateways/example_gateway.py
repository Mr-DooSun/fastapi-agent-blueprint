# -*- coding: utf-8 -*-
from typing import Any, Dict

from src._core.infrastructure.http.http_client import HttpClient


class ExampleApiGateway:
    def __init__(self, http_client: HttpClient, base_url: str) -> None:
        self.http_client = http_client
        self.base_url = base_url

    async def get_data(self, resource_id: str) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.get(
                f"{self.base_url}/resources/{resource_id}",
                headers={"Authorization": "Bearer token"},
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def create_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.post(
                f"{self.base_url}/resources",
                json=data,
                headers={"Authorization": "Bearer token"},
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def update_data(
        self, resource_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        async with self.http_client.session() as session:
            async with session.put(
                f"{self.base_url}/resources/{resource_id}",
                json=data,
                headers={"Authorization": "Bearer token"},
            ) as response:
                response.raise_for_status()
                return await response.json()

    async def delete_data(self, resource_id: str) -> bool:
        async with self.http_client.session() as session:
            async with session.delete(
                f"{self.base_url}/resources/{resource_id}",
                headers={"Authorization": "Bearer token"},
            ) as response:
                response.raise_for_status()
                return True
