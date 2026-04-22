from typing import Protocol, List, Optional
from examples.todo.domain.dtos.todo_dto import TodoDTO

class TodoRepositoryProtocol(Protocol):
    async def create(self, todo: TodoDTO) -> TodoDTO:
        ...

    async def get(self, id: str) -> Optional[TodoDTO]:
        ...

    async def list(self) -> List[TodoDTO]:
        ...

    async def update(self, id: str, todo: TodoDTO) -> TodoDTO:
        ...

    async def delete(self, id: str) -> None:
        ...