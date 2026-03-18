import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app

client = TestClient(app)

MOCK_ID = uuid.uuid4()

@patch("backend.services.custom.CustomComponentService.get_indicators", new_callable=AsyncMock)
def test_get_indicators(mock_get):
    mock_get.return_value = {"total": 0, "items": []}
    response = client.get("/api/v1/custom/indicators")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}

@patch("backend.services.custom.CustomComponentService.create_indicator", new_callable=AsyncMock)
def test_create_indicator(mock_create):
    mock_item = {
        "id": str(MOCK_ID),
        "name": "MACD",
        "description": "Moving Average Convergence Divergence",
        "formula": "def calc(): return True",
        "parameters": {},
        "category": "trend",
        "is_public": False,
        "author_id": str(uuid.uuid4()),
        "usage_count": 0
    }
    
    class MockResult:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    mock_create.return_value = MockResult(**mock_item)
    
    payload = {
        "name": "MACD",
        "formula": "def calc(): return True",
        "category": "trend"
    }
    
    response = client.post("/api/v1/custom/indicators", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "MACD"
    assert data["formula"] == "def calc(): return True"
