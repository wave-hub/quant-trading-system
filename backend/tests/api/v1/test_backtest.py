import uuid
import pytest
from httpx import AsyncClient
from backend.main import app
from unittest.mock import patch, AsyncMock

MOCK_ID = uuid.uuid4()
MOCK_STRAT_ID = uuid.uuid4()

@patch("backend.services.backtest.BacktestService.create_task", new_callable=AsyncMock)
@patch("backend.api.v1.backtest.routes.BackgroundTasks.add_task")
def test_create_and_run_backtest(mock_bg_task, mock_create):
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    class MockTask:
        def __init__(self, **kwargs):
            for k, v in kwargs.items(): setattr(self, k, v)
            
    mock_create.return_value = MockTask(
        id=MOCK_ID,
        strategy_id=MOCK_STRAT_ID,
        name="Test Task",
        start_date="2025-01-01",
        end_date="2025-12-31",
        initial_capital=100000.0,
        status="pending",
        progress=0
    )
    
    payload = {
        "strategy_id": str(MOCK_STRAT_ID),
        "name": "Test Task",
        "start_date": "2025-01-01",
        "end_date": "2025-12-31",
        "initial_capital": 100000.0,
        "config": {}
    }
    
    response = client.post("/api/v1/backtest/", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Task"
    assert data["status"] == "pending"
    assert mock_create.called
    assert mock_bg_task.called
