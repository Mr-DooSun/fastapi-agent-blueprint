# -*- coding: utf-8 -*-
import json

import pika

from src.core.infrastructure.messaging.rabbitmq_manager import RabbitMQManager


class RabbitMQPublisher:
    def __init__(self, rabbitmq_manager: RabbitMQManager):
        self.rabbitmq_manager = rabbitmq_manager

    def send_message(self, queue_name: str, body: dict):
        try:
            self.rabbitmq_manager._ensure_channel()
            channel = self.rabbitmq_manager.channel

            channel.queue_declare(queue=queue_name, durable=True)

            channel.basic_publish(
                exchange="",
                routing_key=queue_name,
                body=json.dumps(body),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            print(f"[x] Sent message to {queue_name}")

        except Exception as e:
            print(f"Failed to send message: {e}")
            self.rabbitmq_manager._connect()
            self.send_message(queue_name, body)
