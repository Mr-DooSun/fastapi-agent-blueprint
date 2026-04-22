from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class TodoDTO(BaseModel):
    id: str 
    title: str
    description: Optional[str] = None
    done: bool = False
    created_at: datetime
    updated_at: datetime