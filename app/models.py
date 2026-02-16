# app/schemas.py
from pydantic import BaseModel, EmailStr, constr, conint
from typing import Optional

#----------------------------------Item Models------------------------------------------------

class ItemClass(BaseModel):
    name:str
    brand:str
    light:      Optional[int] = None
    dark:       Optional[int] = None
    bright:     Optional[int] = None
    warm:       Optional[int] = None
    cool:       Optional[int] = None
    breathable: Optional[int] = None
    cozy:       Optional[int] = None
    lightweight:Optional[int] = None
    fancy:      Optional[int] = None
    casual:     Optional[int] = None
    business:   Optional[int] = None
    lounge:     Optional[int] = None
    evening:    Optional[int] = None
    minimalist: Optional[int] = None
    vintage:    Optional[int] = None
    modern:     Optional[int] = None
    soft:       Optional[int] = None
    comfortable:Optional[int] = None
    layerable:  Optional[int] = None
    img_url:str

def item_return(item):
    return{
        "id": str(item["_id"]),
        "name": item["name"],
        "brand": item["brand"],
        "light": item["light"],
        "dark": item["dark"],
        "bright": item["bright"],
        "warm": item["warm"],
        "cool": item["cool"],
        "lightweight": item["lightweight"],
        "fancy": item["fancy"],
        "casual": item["casual"],
        "business": item["business"],
        "lounge": item["lounge"],
        "evening": item["evening"],
        "minimalist": item["minimalist"],
        "vintage": item["vintage"],
        "modern": item["modern"],
        "soft": item["soft"],
        "comfortable": item["comfortable"],
        "layerable": item["layerable"],
        "img_url": item["img_url"]
    }

def return_via_id(all_items,value):
    return [item_return(item) for item in all_items if (item.get("id") == value)]

def all_items(all_items):
    return [item_return(item) for item in all_items]