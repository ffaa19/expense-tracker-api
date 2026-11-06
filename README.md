# Expense Tracker API

A RESTful Expense Tracker API built with Python, FastAPI, and SQLAlchemy. The application allows users to manage their expenses, filter them by category, and generate monthly spending summaries.

The API also implements user authentication and authorization using JWT access tokens, ensuring that each user can access and manage only their own expenses.

**Live API:** https://expense-tracker-api-8tj2.onrender.com

**Interactive API Documentation:** https://expense-tracker-api-8tj2.onrender.com/docs

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite (local development)
- PostgreSQL (production)
- JWT (PyJWT)
- Argon2 (password hashing)
- Uvicorn
- pytest
- FastAPI TestClient

## Features

### Expense Management
- Create new expenses.
- Retrieve all expenses.
- Filter expenses by category.
- Generate monthly spending summaries by category.
- Delete expenses.
- Validate incoming data using Pydantic.

### Authentication and Authorization
- Register new users with email and password.
- Hash passwords securely using Argon2.
- Authenticate users through JWT access tokens.
- Protect expense endpoints using bearer-token authentication.
- Associate each expense with its owner.
- Enforce user-specific data access and prevent unauthorized access to other users' expenses.

## Project Structure

```text
expense-tracker/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── security.py
├── test_main.py
├── test_security.py
├── test_jwt.py
├── requirements.txt
├── Procfile
├── README.md
└── .gitignore
```

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Authenticate a user and receive a JWT |

### Expense Management

All expense endpoints require a valid JWT bearer token.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/expenses` | Create an expense |
| GET | `/expenses` | Retrieve the authenticated user's expenses |
| GET | `/expenses/category/{category}` | Filter expenses by category |
| GET | `/expenses/summary?year={year}&month={month}` | Get monthly spending totals by category |
| DELETE | `/expenses/{expense_id}` | Delete an expense owned by the authenticated user |

## Security

- Passwords are never stored as plain text. They are hashed using Argon2.
- JWT access tokens are used to authenticate requests.
- Tokens have a 30-minute expiration time.
- Protected endpoints verify the token and identify the authenticated user.
- Database queries restrict expense access to the authenticated user's records.
- Unauthorized requests are rejected.

## Validation

Pydantic schemas validate incoming data, including:

- Positive expense amounts.
- Non-empty category and description fields.
- Valid date values.
- Minimum password length.

## Installation and Local Setup

1. Clone the repository:

```bash
git clone https://github.com/ffaa19/expense-tracker-api.git
```

2. Navigate to the project directory:

```bash
cd expense-tracker-api
```

3. Install dependencies:

```bash
py -m pip install