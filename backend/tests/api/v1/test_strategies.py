import uuid
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app

client = TestClient(app)

MOCK_ID = uuid.uuid4()

@patch("backend.services.strategy.StrategyService.get_strategies", new_callable=AsyncMock)
def test_get_strategies(mock_get_strategies):
    mock_get_strategies.return_value = {"total": 0, "items": []}
    response = client.get("/api/v1/strategies")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}

@patch("backend.services.strategy.StrategyService.create_strategy", new_callable=AsyncMock)
def test_create_strategy(mock_create):
    mock_strategy = {
        "id": str(MOCK_ID),
        "name": "Test Strategy",
        "category": "Test",
        "description": "Desc",
        "is_visual": False,
        "parameters": {},
        "code": "print('hello')",
        "status": "draft",
        "version": 1,
        "user_id": str(uuid.uuid4())
    }
    
    # Needs to return an object that behaves like a model instance for serialization
    class MockStrategy:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    
    mock_create.return_value = MockStrategy(**mock_strategy)
    
    payload = {
        "name": "Test Strategy",
        "type": "code",
        "code": "print('hello')"
    }
    
    response = client.post("/api/v1/strategies", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Strategy"
    assert data["code"] == "print('hello')"
