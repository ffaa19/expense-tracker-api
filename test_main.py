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

@pytest.fixture
def auth_headers(reset_database):
    # Register a test user
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )

    # Log in
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }

# Reset the test database before every test
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

def test_create_expense(auth_headers):
    response = client.post(
        "/expenses",
        json={
            "amount": 25.5,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    assert response.status_code == 201

    data = response.json()

    assert data["amount"] == 25.5
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["date"] == "2026-10-31"
    assert "id" in data
    assert "created_at" in data
def test_get_expenses(auth_headers):
    # First, create an expense
    client.post(
        "/expenses",
        json={
            "amount": 30,
            "category": "Food",
            "description": "Dinner",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    # Then, retrieve all expenses
    response = client.get("/expenses", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["amount"] == 30
def test_filter_expenses_by_category(auth_headers):
    # Create a Food expense
    client.post(
        "/expenses",
        json={
            "amount": 20,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    # Create a Transport expense
    client.post(
        "/expenses",
        json={
            "amount": 5,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    # Retrieve only Food expenses
    response = client.get("/expenses/category/Food", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category"] == "Food"
    assert data[0]["amount"] == 20
def test_monthly_summary(auth_headers):
    # Create two Food expenses
    client.post(
        "/expenses",
        json={
            "amount": 25.5,
            "category": "Food",
            "description": "Lunch",
            "date": "2026-10-10"
        },
        headers=auth_headers
    )

    client.post(
        "/expenses",
        json={
            "amount": 10,
            "category": "Food",
            "description": "Coffee",
            "date": "2026-10-15"
        },
        headers=auth_headers
    )

    # Create a Transport expense
    client.post(
        "/expenses",
        json={
            "amount": 5,
            "category": "Transport",
            "description": "Bus",
            "date": "2026-10-20"
        },
        headers=auth_headers
    )

    # Get the summary for October 2026
    response = client.get("/expenses/summary?year=2026&month=10", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()

    assert data["Food"] == 35.5
    assert data["Transport"] == 5
def test_delete_expense(auth_headers):
    # Create an expense first
    create_response = client.post(
        "/expenses",
        json={
            "amount": 15,
            "category": "Food",
            "description": "Snack",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    # Get the ID of the created expense
    expense_id = create_response.json()["id"]

    # Delete the expense
    response = client.delete(f"/expenses/{expense_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["message"] == "Expense deleted successfully"

    # Verify that the expense is gone
    get_response = client.get(
    "/expenses",
    headers=auth_headers
)

    assert get_response.status_code == 200
    assert get_response.json() == []

def test_create_expense_with_invalid_amount(auth_headers):
    response = client.post(
        "/expenses",
        json={
            "amount": -10,
            "category": "Food",
            "description": "Invalid expense",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    assert response.status_code == 422

def test_delete_nonexistent_expense(auth_headers):
    response = client.delete("/expenses/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"

def test_users_cannot_access_each_others_expenses(auth_headers):
    # Create an expense as User A
    create_response = client.post(
        "/expenses",
        json={
            "amount": 50,
            "category": "Food",
            "description": "User A's lunch",
            "date": "2026-10-31"
        },
        headers=auth_headers
    )

    expense_id = create_response.json()["id"]

    # Register User B
    client.post(
        "/auth/register",
        json={
            "email": "userb@example.com",
            "password": "UserBPassword123"
        }
    )

    # Log in as User B
    login_response = client.post(
        "/auth/login",
        json={
            "email": "userb@example.com",
            "password": "UserBPassword123"
        }
    )

    token_b = login_response.json()["access_token"]

    headers_b = {
        "Authorization": f"Bearer {token_b}"
    }

    # User B tries to retrieve all expenses
    get_response = client.get(
        "/expenses",
        headers=headers_b
    )

    assert get_response.status_code == 200
    assert get_response.json() == []

    # User B tries to delete User A's expense
    delete_response = client.delete(
        f"/expenses/{expense_id}",
        headers=headers_b
    )

    assert delete_response.status_code == 404

    # Verify User A still owns the expense
    verify_response = client.get(
        "/expenses",
        headers=auth_headers
    )

    assert len(verify_response.json()) == 1