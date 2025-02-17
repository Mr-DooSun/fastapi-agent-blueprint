# -*- coding: utf-8 -*-
from fastapi import FastAPI

from src.core.middleware.exception_handler import ExceptionMiddleware
from src.server.infrastructure.di.container import ServerContainer

container = None


def create_container():
    container = ServerContainer()
    container.wire(packages=["src.server.application.controllers"])

    container.config.from_yaml("./config.yml")

    return container


def create_app():
    global container
    container = create_container()

    app = FastAPI(docs_url="/docs")
    app.add_middleware(ExceptionMiddleware)

    return app


app = create_app()
