import pytest
from unittest.mock import MagicMock, patch
from bson import ObjectId
from test.conftest import make_mock_db, FAKE_ID

FAKE_ID2 = str(ObjectId())
FAKE_ID3 = str(ObjectId())
FAKE_ID4 = str(ObjectId())


@pytest.fixture(autouse=True)
def patch_db(mock_db):
    db, _, _ = mock_db
    with patch("app.consumer.db", db):
        yield db


def _recom(n=4, feedback=-1):
    data = {f"rec{i}_id": [FAKE_ID, FAKE_ID2, FAKE_ID3, FAKE_ID4][i - 1] for i in range(1, n + 1)}
    data.update({f"attr{i}": ["light", "bright", "cool", "casual"][i - 1] for i in range(1, n + 1)})
    data["feedback"] = feedback
    return data


def test_start_train_4_ids(mock_db):
    from app.consumer import start_train
    db, collection, item = mock_db
    result = start_train(_recom(4))
    assert result is not None
    assert collection.update_one.called


def test_start_train_3_ids(mock_db):
    from app.consumer import start_train
    db, collection, item = mock_db
    result = start_train(_recom(3))
    assert result is not None


def test_start_train_positive_feedback(mock_db):
    from app.consumer import start_train
    db, collection, item = mock_db
    result = start_train(_recom(4, feedback=1))
    assert result is not None
    call_args = collection.update_one.call_args[0][1]["$set"]
    assert call_args["light"] == item["light"] + (1 * 0.5)


def test_start_train_negative_feedback(mock_db):
    from app.consumer import start_train
    db, collection, item = mock_db
    result = start_train(_recom(4, feedback=-1))
    set_doc = collection.update_one.call_args[0][1]["$set"]
    assert set_doc["light"] == item["light"] + (-1 * 0.5)


def test_update_values_invalid_id(mock_db):
    from app.consumer import update_values
    db, collection, _ = mock_db
    result = update_values(["light"], ["not-a-valid-id"], -1, 0.5)
    assert result is None
    collection.find_one.assert_not_called()


def test_update_values_item_not_found(mock_db):
    from app.consumer import update_values
    db, collection, _ = mock_db
    collection.find_one.return_value = None
    result = update_values(["light"], [FAKE_ID], -1, 0.5)
    assert result is None


def test_update_values_updates_correct_fields(mock_db):
    from app.consumer import update_values
    db, collection, item = mock_db
    update_values(["light", "cool"], [FAKE_ID], 1, 0.5)
    set_doc = collection.update_one.call_args[0][1]["$set"]
    assert set_doc["light"] == item["light"] + 0.5
    assert set_doc["cool"] == item["cool"] + 0.5
