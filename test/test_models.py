import pytest
from bson import ObjectId

SAMPLE_ITEM = {
    "_id": ObjectId(),
    "name": "Shirt", "brand": "BrandX",
    "light": 5, "dark": 3, "bright": 4, "warm": 2,
    "cool": 6, "fancy": 1, "casual": 7, "business": 2,
    "evening": 3, "minimalist": 4, "vintage": 5,
    "modern": 6, "floral": 1, "colourful": 2,
    "img_url": "http://example.com/img.jpg"
}


def test_item_return_fields():
    from app.models import item_return
    result = item_return(SAMPLE_ITEM)
    assert result["id"] == str(SAMPLE_ITEM["_id"])
    assert result["name"] == "Shirt"
    assert result["light"] == 5
    assert result["img_url"] == "http://example.com/img.jpg"


def test_item_return_all_keys():
    from app.models import item_return
    result = item_return(SAMPLE_ITEM)
    expected_keys = {"id", "name", "brand", "light", "dark", "bright", "warm",
                     "cool", "fancy", "casual", "business", "evening",
                     "minimalist", "vintage", "modern", "floral", "colourful", "img_url"}
    assert set(result.keys()) == expected_keys


def test_all_items():
    from app.models import all_items
    result = all_items([SAMPLE_ITEM])
    assert len(result) == 1
    assert result[0]["name"] == "Shirt"


def test_all_items_empty():
    from app.models import all_items
    assert all_items([]) == []


def test_return_via_id_no_match():
    from app.models import return_via_id
    result = return_via_id([SAMPLE_ITEM], "nonexistent-id")
    assert result == []


def test_item_class_optional_fields():
    from app.models import ItemClass
    item = ItemClass(name="T-Shirt", brand="BrandY", img_url="http://x.com/img.jpg")
    assert item.light is None
    assert item.casual is None


def test_item_class_with_values():
    from app.models import ItemClass
    item = ItemClass(name="T-Shirt", brand="BrandY", light=5, casual=3, img_url="http://x.com/img.jpg")
    assert item.light == 5
    assert item.casual == 3
