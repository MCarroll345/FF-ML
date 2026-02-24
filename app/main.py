from fastapi import FastAPI, APIRouter, Body, Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from dotenv import dotenv_values
from .config import db 
from .models import *

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

shirts_db = db["shirts"]

weighting = {}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/{c1}/{c2}/{c3}/{c4}/{itemid}/{yn}/train")
async def get_recom(c1: str,c2: str,c3: str,c4: str, itemid: str, yn: int):
    try:
        return start_train(itemid,c1,c2,c3,c4,yn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendation: {e}")

def start_train(itemid, c1, c2, c3, c4, yn):
    find = db["shirts"].find_one({"_id": ObjectId(itemid)})
    item = item_return(find)
    weight = 0.5
    var_list = [c1,c2,c3,c4]
    up = update_values(var_list, itemid, item, yn, weight)
    return up

def update_values(var_list, itemid, item, yn, weight):
    updates = {}
    for var in var_list:
        old = item.get(var)
        updates[var] = old + (yn*weight)

    result = shirts_db.update_one(
        {'_id': ObjectId(itemid)},
        {'$set': updates}
    )
    print("Matched documents:", result.matched_count)
    print("Modified documents:", result.modified_count)
    return item

def chooseRandVar():
    
    return 0