import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId

FAKE_ID = str(ObjectId())

def make_mock_db(item_data=None):
    item = item_data or {
        "_id": ObjectId(FAKE_ID),
        "name": "Test Item", "brand": "Brand",
        "light": 5, "dark": 3, "bright": 4, "warm": 2,
        "cool": 6, "fancy": 1, "casual": 7, "business": 2,
        "evening": 3, "minimalist": 4, "vintage": 5,
        "modern": 6, "floral": 1, "colourful": 2,
        "img_url": "http://example.com/img.jpg"
    }
    collection = MagicMock()
    collection.find_one.return_value = item
    collection.update_one.return_value = MagicMock(matched_count=1, modified_count=1)

    mock_db = MagicMock()
    mock_db.list_collection_names.return_value = ["tops"]
    mock_db.__getitem__.return_value = collection
    return mock_db, collection, item

@pytest.fixture
def mock_db():
    db, collection, item = make_mock_db()
    return db, collection, item
