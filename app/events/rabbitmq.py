import aio_pika
from tenacity import retry, wait_fixed, stop_after_attempt

from app.config import settings


class RabbitMQClient:
    _connection = None

    @classmethod
    @retry(wait=wait_fixed(2), stop=stop_after_attempt(5))
    async def get_connection(cls):
        if cls._connection is None:
            cls._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        return cls._connection

    @staticmethod
    async def publish(queue_name: str, message_body: bytes):
        conn = await RabbitMQClient.get_connection()
        channel = await conn.channel()
        queue = await channel.declare_queue(queue_name, durable=True)
        await channel.default_exchange.publish(
            aio_pika.Message(body=message_body), routing_key=queue.name
        )
