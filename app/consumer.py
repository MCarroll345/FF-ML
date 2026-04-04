import aio_pika
from aio_pika import ExchangeType
import asyncio
import json
import os
from .config import db 
from bson import ObjectId
from dotenv import load_dotenv
from datetime import datetime
import random

load_dotenv()

ATTR_LIST = [
  'light',
  'dark',
  'colourful',
  'warm',
  'cool',
  'light',
  'fancy',
  'casual',
  'business',
  'evening',
  'minimalist',
  'vintage',
  'modern',
  'floral',
]

RABBIT_URL = os.getenv("RABBIT_URL")
EXCHANGE_NAME = os.getenv("EXCHANGE_NAME", "recom_topic")
QUEUE_NAME = os.getenv("RECOM_QUEUE", "recom_queue")

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
                            print(f"In")
                            raw = message.body
                            if isinstance(raw, (bytes, bytearray)):
                                raw = raw.decode("utf-8")

                            payload = json.loads(raw)

                            event_type = None
                            data = None

                            if isinstance(payload, dict):
                                event_type = payload.get("event_type")
                                data = payload.get("data") or {}

                                # unwrap nested data if needed
                                if isinstance(data, dict) and "data" in data:
                                    data = data.get("data") or {}

                            result = start_train(data)
                            #print(f"Feedback taken and processed: {data}")

                        except json.JSONDecodeError as e:
                            print("Invalid JSON in message body:", e)
                        except Exception as e:
                            print("Failed to process recom message:", e)
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

def start_train(recomData):
    print(f"Received recom data: {recomData}")
    itemIDs = [recomData[f"rec{i}_id"] for i in range(1, 5) if f"rec{i}_id" in recomData]
    print(f"Received recom data: {itemIDs}")
    var_list = [recomData[f"attr{i}"] for i in range(1, 5) if f"attr{i}" in recomData]
    print(f"Received recom data: {var_list}")
    feedback = [recomData["feedback"]]
    print(f"Received recom data: {feedback}")
    weight = 0.5
    up = update_values(var_list, itemIDs, feedback, weight)
    return up

def update_values(var_list, itemIDs, feedback, weight):
    last_updated_item = None

    for itemid in itemIDs:
        if not ObjectId.is_valid(itemid):
            continue

        obj_id = ObjectId(itemid)
        for collection_name in db.list_collection_names():
            collection = db[collection_name]
            item = collection.find_one({"_id": obj_id})
            if not item:
                continue

            updates = {}
            for var in var_list:
                old = item.get(var)
                updates[var] = old + (feedback[0] * weight)

            if feedback[0] == -1:
                for rando in range(1, 4):
                    rand_attr = random.choice(ATTR_LIST)
                    if rand_attr not in var_list:
                        old = item.get(rand_attr)
                        updates[rand_attr] = old + (1 * weight)
                        print(f"Updated {rand_attr}")

            if not updates:
                continue

            result = collection.update_one(
                {"_id": obj_id},
                {"$set": updates}
            )
            print(f"[{collection_name}] Matched documents:", result.matched_count)
            print(f"[{collection_name}] Modified documents:", result.modified_count)
            last_updated_item = collection.find_one({"_id": obj_id})

    return last_updated_item


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Interrupted by user")