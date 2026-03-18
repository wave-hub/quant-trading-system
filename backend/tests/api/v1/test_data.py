from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from backend.main import app

client = TestClient(app)

@patch("backend.services.data.DataService.get_stocks", new_callable=AsyncMock)
def test_get_stocks_empty(mock_get_stocks):
    mock_get_stocks.return_value = {"total": 0, "items": []}
    response = client.get("/api/v1/data/market/stocks")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}

@patch("backend.services.data.DataService.get_market_data", new_callable=AsyncMock)
def test_get_market_data_empty(mock_get_market_data):
    mock_get_market_data.return_value = {"total": 0, "items": []}
    response = client.get("/api/v1/data/market/history?symbol=000001.SZ")
    assert response.status_code == 200
    assert response.json() == {"total": 0, "items": []}

@patch("backend.services.data.DataService.sync_stocks", new_callable=AsyncMock)
def test_sync_stocks(mock_sync_stocks):
    mock_sync_stocks.return_value = 5000
    response = client.post("/api/v1/data/market/sync/stocks")
    assert response.status_code == 200
    assert response.json() == {"message": "success", "synced_count": 5000}

@patch("backend.services.data.DataService.sync_market_data", new_callable=AsyncMock)
def test_sync_history(mock_sync_market_data):
    mock_sync_market_data.return_value = 250
    response = client.post("/api/v1/data/market/sync/history?symbol=000001.SZ")
    assert response.status_code == 200
    assert response.json() == {"message": "success", "synced_count": 250}
