import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# Create a separate in-memory database for testing
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False
)


# Create the tables in the test database
Base.metadata.create_all(bind=test_engine)


# Replace the normal database dependency with the test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# Reset the test database before every test
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def test_create_expense():
    response = client.post(
        "/expenses",
        json={
            "amount": 25.5,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-31"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 25.5
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["date"] == "2026-10-31"
    assert "id" in data
    assert "created_at" in data
def test_get_expenses():
    # First, create an expense
    client.post(
        "/expenses",
        json={
            "amount": 30,
            "category": "Food",
            "description": "Dinner",
            "date": "2026-10-31"
        }
    )

    # Then, retrieve all expenses
    response = client.get("/expenses")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["amount"] == 30
def test_filter_expenses_by_category():
    # Create a Food expense
    client.post(
        "/expenses",
        json={
            "amount": 20,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-31"
        }
    )

    # Create a Transport expense
    client.post(
        "/expenses",
        json={
            "amount": 5,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-10-31"
        }
    )

    # Retrieve only Food expenses
    response = client.get("/expenses/category/Food")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["amount"] == 20
def test_monthly_summary():
    # Create two Food expenses
    client.post(
        "/expenses",
        json={
            "amount": 25.5,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-10"
        }
    )

    client.post(
        "/expenses",
        json={
            "amount": 10,
            "category": "Food",
            "description": "Coffee",
            "date": "2026-10-15"
        }
    )

    # Create a Transport expense
    client.post(
        "/expenses",
        json={
            "amount": 5,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-10-20"
        }
    )

    # Get the summary for October 2026
    response = client.get("/expenses/summary?year=2026&month=10")

    assert response.status_code == 200

    data = response.json()

    assert data["Food"] == 35.5
    assert data["Transport"] == 5
def test_delete_expense():
    # Create an expense first
    create_response = client.post(
        "/expenses",
        json={
            "amount": 15,
            "category": "Food",
            "description": "Snack",
            "date": "2026-10-31"
        }
    )

    # Get the ID of the created expense
    expense_id = create_response.json()["id"]

    # Delete the expense
    response = client.delete(f"/expenses/{expense_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Expense deleted successfully"

    # Verify that the expense is gone
    get_response = client.get("/expenses")

    assert get_response.status_code == 200
    assert get_response.json() == []

def test_create_expense_with_invalid_amount():
    response = client.post(
        "/expenses",
        json={
            "amount": -10,
            "category": "Food",
            "description": "Invalid expense",
            "date": "2026-10-31"
        }
    )

    assert response.status_code == 422

def test_delete_nonexistent_expense():
    response = client.delete("/expenses/9999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"