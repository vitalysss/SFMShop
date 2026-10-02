import json
import logging

import pika

from src.config import RABBITMQ_HOST, RABBITMQ_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueProducer:
    def __init__(
        self,
        host: str = RABBITMQ_HOST,
        port: int = RABBITMQ_PORT,
    ):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                )
            )
            self.channel = self.connection.channel()

            self.channel.queue_declare(
                queue="order_processing",
                durable=True,
            )

            logger.info("Подключение к RabbitMQ установлено")
            return True

        except Exception:
            logger.exception("Ошибка подключения к RabbitMQ")
            return False

    def send_order_task(
        self,
        order_id: int,
        task_type: str,
        data: dict,
    ):
        if not self.channel:
            if not self.connect():
                return False

        try:
            message = {
                "task": task_type,
                "order_id": order_id,
                **data,
            }

            if self.channel is None:
                return False

            self.channel.basic_publish(
                exchange="",
                routing_key="order_processing",
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                ),
            )

            logger.info(
                "Задача отправлена в очередь: %s",
                message,
            )
            return True

        except Exception:
            logger.exception("Ошибка отправки задачи")
            return False

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
