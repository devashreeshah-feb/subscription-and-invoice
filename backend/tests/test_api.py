import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.db.base import Base
from app.api.deps import get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    from init_db import init_db
    db = TestingSessionLocal()
    init_db(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SubFlow API"}

def test_read_plans():
    response = client.get("/api/v1/plans/")
    assert response.status_code == 200
    plans = response.json()
    assert len(plans) == 4
    plan_names = [p["name"] for p in plans]
    assert "Free" in plan_names
    assert "Starter" in plan_names

def test_login_and_me():
    # Login as demo customer
    response = client.post("/api/v1/auth/login", data={"username": "alice@example.com", "password": "password123"})
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Get user profile
    me_resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "alice@example.com"

def test_subscription_flow():
    # Login
    login = client.post("/api/v1/auth/login", data={"username": "alice@example.com", "password": "password123"}).json()
    headers = {"Authorization": f"Bearer {login['access_token']}"}
    
    plans = client.get("/api/v1/plans/").json()
    starter_plan = [p for p in plans if p["name"] == "Starter"][0]
    
    # Create subscription
    sub_resp = client.post("/api/v1/subscriptions/", json={"plan_id": starter_plan["id"], "payment_method_id": "pm_success"}, headers=headers)
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()
    assert sub_data["status"] == "Active"
    
    # Check invoices
    inv_resp = client.get("/api/v1/invoices/", headers=headers)
    assert inv_resp.status_code == 200
    assert len(inv_resp.json()) == 1
