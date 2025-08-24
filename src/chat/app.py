# -*- coding: utf-8 -*-
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from src.core.middleware.exception_middleware import ExceptionMiddleware


def create_app():
    """Chat 도메인 전용 FastAPI 앱 - 마이크로서비스"""
    app = FastAPI(
        title="Chat Service", 
        description="실시간 채팅 마이크로서비스",
        version="1.0.0",
        root_path="/api",
        docs_url="/docs-swagger",
        redoc_url="/docs-redoc"
    )
    
    # 미들웨어 설정
    app.add_middleware(ExceptionMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Chat WebSocket 라우터
    @app.websocket("/v1/ws/chat")
    async def chat_websocket(websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"서버 응답: {data}")
    
    return app


app = create_app()
