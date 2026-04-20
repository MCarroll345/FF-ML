import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from bson import ObjectId
from fastapi.testclient import TestClient
from test.conftest import make_mock_db, FAKE_ID


@pytest.fixture(autouse=True)
def patch_consumer_and_db():
    db, collection, item = make_mock_db()
    with patch("app.consumer.db", db), \
         patch("app.main.db", db), \
         patch("app.consumer._consume_once", new_callable=lambda: lambda: AsyncMock()), \
         patch("app.consumer.consume", new_callable=lambda: lambda: AsyncMock()):
        yield db, collection, item


@pytest.fixture
def client(patch_consumer_and_db):
    with patch("app.main.consumer.consume", new_callable=lambda: lambda: AsyncMock()):
        from app.main import app
        with TestClient(app, raise_server_exceptions=True) as c:
            yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_start_train_main(patch_consumer_and_db):
    db, collection, item = patch_consumer_and_db
    from app.main import start_train
    recom = {
        "rec1_id": FAKE_ID, "rec2_id": FAKE_ID, "rec3_id": FAKE_ID, "rec4_id": FAKE_ID,
        "attr1": "light", "attr2": "bright", "attr3": "cool", "attr4": "casual",
        "feedback": 1
    }
    result = start_train(recom)
    assert result is not None


def test_update_values_main(patch_consumer_and_db):
    db, collection, item = patch_consumer_and_db
    from app.main import update_values
    result = update_values(["light", "cool"], [FAKE_ID], 1, 0.5)
    assert result is not None
    set_doc = collection.update_one.call_args[0][1]["$set"]
    assert set_doc["light"] == item["light"] + 0.5


def test_update_values_invalid_id(patch_consumer_and_db):
    db, collection, _ = patch_consumer_and_db
    from app.main import update_values
    result = update_values(["light"], ["bad-id"], 1, 0.5)
    assert result is None


def test_update_values_item_not_found(patch_consumer_and_db):
    db, collection, _ = patch_consumer_and_db
    collection.find_one.return_value = None
    from app.main import update_values
    result = update_values(["light"], [FAKE_ID], 1, 0.5)
    assert result is None


def test_choose_rand_var():
    from app.main import chooseRandVar
    assert chooseRandVar() == 0
