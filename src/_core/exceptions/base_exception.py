# -*- coding: utf-8 -*-


class BaseCustomException(Exception):
    def __init__(self, status_code: int = 400, message: str = "Not Found"):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"{self.status_code}: {self.message}"
