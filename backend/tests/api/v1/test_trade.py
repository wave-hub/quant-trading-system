import uuid
import pytest
from httpx import AsyncClient
from backend.main import app
from backend.models.trade import Account

MOCK_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000000")

def test_get_accounts():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    response = client.get("/api/v1/trade/accounts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["account_type"] == "simulation"
    assert data[0]["current_capital"] == 1000000.0

def test_place_paper_order():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # 1. Fetch account
    accounts_res = client.get("/api/v1/trade/accounts")
    account_id = accounts_res.json()[0]["id"]
    
    # 2. Place a mock buy order
    payload = {
        "account_id": account_id,
        "symbol": "AAPL",
        "side": "buy",
        "order_type": "market",
        "quantity": 100,
        "price": 150.0  # mock price for execution
    }
    
    res = client.post("/api/v1/trade/orders", json=payload)
    assert res.status_code == 201
    order_data = res.json()
    assert order_data["status"] == "filled"
    assert order_data["filled_quantity"] == 100
    assert order_data["avg_fill_price"] == 150.0
    
    # 3. Check position
    pos_res = client.get(f"/api/v1/trade/positions/{account_id}")
    positions = pos_res.json()
    assert len(positions) >= 1
    
    # 4. Attempt sell order (Paper Trading Simulation)
    sell_payload = {
        "account_id": account_id,
        "symbol": "AAPL",
        "side": "sell",
        "order_type": "market",
        "quantity": 50,
        "price": 160.0
    }
    sell_res = client.post("/api/v1/trade/orders", json=sell_payload)
    assert sell_res.status_code == 201
    assert sell_res.json()["status"] == "filled"
