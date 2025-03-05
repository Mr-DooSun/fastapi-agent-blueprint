# -*- coding: utf-8 -*-
from pydantic import BaseModel


class PaginationResponse(BaseModel):
    current_page: int
    page_size: int
    total_items: int
    total_pages: int
    has_previous: bool
    has_next: bool
    next_page: int
    previous_page: int
