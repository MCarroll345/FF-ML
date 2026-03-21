from fastapi import FastAPI, APIRouter, Body, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import dotenv_values
from .config import db 
import aio_pika
import json
import asyncio
from .models import *
from . import consumer
from contextlib import asynccontextmanager

#******************************RabbitMQ stuff******************************************
@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks = []

    try:
        print("Starting background RabbitMQ consumers")

        # notifications consumer (inserts into notifications_collection)
        ml_task = asyncio.create_task(consumer.consume())
        tasks.append(ml_task)

        app.state.consumer_tasks = tasks
    except Exception as e:
        print(f"ERROR: Failed to start consumer tasks: {e}")

    try:
        yield
    finally:
        for t in getattr(app.state, "consumer_tasks", []):
            try:
                t.cancel()
            except Exception:
                pass
        # Await cancellation
        for t in getattr(app.state, "consumer_tasks", []):
            try:
                await t
            except asyncio.CancelledError:
                pass

app = FastAPI(title="ML API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/{c1}/{c2}/{c3}/{c4}/{itemid}/{yn}/train")
async def get_recom(c1: str,c2: str,c3: str,c4: str, itemid: str, yn: int):
    try:
        return start_train(itemid,c1,c2,c3,c4,yn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendation: {e}")

def start_train(recomData):
    itemIDs = [ recomData["rec1_id"], recomData["rec2_id"], recomData["rec3_id"], recomData["rec4_id"] ]
    var_list = [recomData["attr1"], recomData["attr2"], recomData["attr3"], recomData["attr4"]]
    feedback = recomData["feedback"]
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
                updates[var] = old + (yn*weight)

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

def chooseRandVar():
    
    return 0