import asyncio
import json
from aio_pika import connect_robust, IncomingMessage
from app.config import settings
from app.instrumentation.tracing import get_tracers


async def handle_user_created(message: IncomingMessage) -> None:
    with message.process():
        payload = json.loads(message.body)
        user_id = payload.get("id")
        with get_tracers().start_as_current_span("consumer.user_created"):
            # Example: fetch user, send welcome email, etc.
            print(f"[Consumer] New user created: {user_id}")

async def main():
    connection = await connect_robust(settings.RABBITMQ_URL)
    channel = await connection.channel()
    queue = await channel.declare_queue("user.created", durable=True)
    await queue.consume(handle_user_created)
    print(" [*] Waiting for user.created messages. To exit press CTRL+C")
    await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())