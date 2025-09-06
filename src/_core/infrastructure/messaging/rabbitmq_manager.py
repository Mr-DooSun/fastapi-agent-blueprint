# -*- coding: utf-8 -*-
# src/core/infrastructure/messaging/rabbitmq_manager.py
import pika


class RabbitMQManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self._connect()

    def _connect(self):
        if self.connection and self.connection.is_open:
            return

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host, port=self.port)
        )
        self.channel = self.connection.channel()

    def _ensure_channel(self):
        if not self.channel or self.channel.is_closed:
            self._connect()

    def close(self):
        if self.connection and self.connection.is_open:
            self.connection.close()
