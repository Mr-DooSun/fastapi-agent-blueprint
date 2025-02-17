# -*- coding: utf-8 -*-


class BaseCustomException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code

    def __str__(self):
        return f"{self.status_code}: {self.message}"
