# -*- coding: utf-8 -*-
from abc import ABC

from pydantic import BaseModel


class Entity(ABC, BaseModel):
    class Config:
        use_enum_values = True
