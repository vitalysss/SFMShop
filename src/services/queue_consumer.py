import json
import logging

import pika

from src.config import RABBITMQ_HOST, RABBITMQ_PORT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def send_email(user_email: str, message: str):
    logger.info("Email для %s: %s", user_email, message)


def update_stock(items: list):
    logger.info("Обновление склада: %s", items)


def generate_report(order_id: int):
    logger.info("Генерация отчёта для заказа %s", order_id)


class QueueConsumer:
    def __init__(
        self,
        host: str = RABBITMQ_HOST,
        port: int = RABBITMQ_PORT,
    ):
        self.host = host
        self.port = port
        self.connection = None
        self.channel = None
        self.max_retries = 3

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
            self.channel.queue_declare(
                queue="order_processing_errors",
                durable=True,
            )

            self.channel.basic_qos(prefetch_count=1)

            logger.info("Подключение к RabbitMQ установлено")
            return True
        except Exception:
            logger.exception("Ошибка подключения к RabbitMQ")
            return False

    def process_message(self, ch, method, properties, body):
        retry_count = properties.headers.get("x-retry-count", 0) if properties.headers else 0

        try:
            message = json.loads(body)
            task = message.get("task")
            order_id = message.get("order_id")
            if task == "send_email":
                user_email = message.get("user_email")
                send_email(user_email, f"Заказ {order_id} создан")

            elif task == "update_stock":
                items = message.get("items", [])
                update_stock(items)

            elif task == "generate_report":
                generate_report(order_id)

            else:
                raise ValueError(f"Неизвестный тип задачи: {task}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

            logger.info(
                "Задача %s для заказа %s обработана",
                task,
                order_id,
            )

        except Exception:
            logger.exception("Ошибка обработки задачи")

            if retry_count < self.max_retries:
                retry_count += 1

                logger.warning(
                    "Повторная попытка %s/%s",
                    retry_count,
                    self.max_retries,
                )

                ch.basic_publish(
                    exchange="",
                    routing_key="order_processing",
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=2, headers={"x-retry-count": retry_count}
                    ),
                )

                ch.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False,
                )
            else:
                ch.basic_publish(
                    exchange="",
                    routing_key="order_processing_errors",
                    body=body,
                    properties=pika.BasicProperties(delivery_mode=2),
                )

                ch.basic_ack(delivery_tag=method.delivery_tag)

                logger.error(
                    "Задача отправлена в очередь ошибок после %s попыток",
                    self.max_retries,
                )

    def start_consuming(self):
        if not self.connect():
            return

        self.channel.basic_consume(
            queue="order_processing",
            on_message_callback=self.process_message,
        )

        logger.info("Ожидание сообщений в очереди order_processing...")

        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            self.channel.stop_consuming()

            if self.connection and not self.connection.is_closed:
                self.connection.close()


if __name__ == "__main__":
    consumer = QueueConsumer()
    consumer.start_consuming()
