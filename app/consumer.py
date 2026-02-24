import aio_pika
from aio_pika import ExchangeType
import asyncio
import json
import os
from dotenv import load_dotenv
from datetime import datetime
from .main import start_train

load_dotenv()

RABBIT_URL = os.getenv("RABBIT_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "recom_topic")
QUEUE_NAME = os.getenv("RECOM_QUEUE", "recom_queue")

from .configurations import notifications_collection

if not RABBIT_URL:
    raise RuntimeError("RABBIT_URL is not set. Export it or add it to a .env file.")

async def _consume_once():
    print(f"Connecting to RabbitMQ at {RABBIT_URL}")
    connection = await aio_pika.connect_robust(RABBIT_URL)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(EXCHANGE_NAME, ExchangeType.TOPIC, durable=False)
        queue = await channel.declare_queue(QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key="#")

        print(f"Waiting for messages on '{QUEUE_NAME}' bound to exchange '{EXCHANGE_NAME}'...")

        try:
            async with queue.iterator() as q:
                async for message in q:
                    async with message.process():
                        try:
                            raw = message.body
                            if isinstance(raw, (bytes, bytearray)):
                                raw = raw.decode("utf-8")

                            payload = json.loads(raw)

                            event_type = None
                            user_id = None
                            data = None

                            if isinstance(payload, dict):
                                event_type = payload.get("event_type")
                                data = payload.get("data") or {}

                                # unwrap nested data if needed
                                if isinstance(data, dict) and "data" in data:
                                    data = data.get("data") or {}

                            result = start_train(data)
                            print(f"Feedback taken and processed: {data}")

                        except json.JSONDecodeError as e:
                            print("Invalid JSON in message body:", e)
                        except Exception as e:
                            print("Failed to process notification message:", e)
        except asyncio.CancelledError:
            print("Recom consumer cancelled")



async def consume():
    # Keep the consumer alive if connection drops
    while True:
        try:
            await _consume_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print(f"Recom consumer loop error: {exc}; retrying in 5s")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Interrupted by user")