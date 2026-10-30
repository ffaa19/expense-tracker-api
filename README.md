# Expense Tracker API

A RESTful Expense Tracker API built with Python, FastAPI, and SQLAlchemy. It allows users to manage expenses, filter them by category, and generate monthly spending summaries.

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite (local development)
- PostgreSQL (deployment)
- Pydantic
- Uvicorn

## Features

- Create new expenses.
- Retrieve all expenses.
- Filter expenses by category.
- Generate monthly spending summaries by category.
- Delete expenses.
- Validate incoming data using Pydantic.

## Project Structure

```text
expense-tracker/
├── main.py
├── database.py
├── models.py
├── schemas.py
├── requirements.txt
├── Procfile
└── README.md
```

## Installation and Setup

1. Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

2. Navigate to the project directory:

```bash
cd expense-tracker
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
uvicorn main:app --reload
```

5. Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/expenses` | Create an expense |
| GET | `/expenses` | Retrieve all expenses |
| GET | `/expenses/category/{category}` | Filter expenses by category |
| GET | `/expenses/summary?year={year}&month={month}` | Get monthly spending totals by category |
| DELETE | `/expenses/{expense_id}` | Delete an expense |

## Validation

The API uses Pydantic to validate incoming data, including positive expense amounts, non-empty category and description fields, and valid dates.

## Deployment

The application will be deployed using Railway with PostgreSQL as its production database.

**Live API:** To be added after deployment.

**Interactive Documentation:** To be added after deployment.