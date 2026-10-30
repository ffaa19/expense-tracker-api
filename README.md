# Expense Tracker API

A RESTful Expense Tracker API built with Python, FastAPI, and SQLAlchemy. The application allows users to manage expenses, filter them by category, and generate monthly spending summaries.

**Live API:** https://expense-tracker-api-8tj2.onrender.com

**Interactive API Documentation:** https://expense-tracker-api-8tj2.onrender.com/docs

## Technologies Used

- Python
- FastAPI
- SQLAlchemy
- SQLite (local development)
- PostgreSQL (production)
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
├── README.md
└── .gitignore
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

The API uses Pydantic to validate incoming data, including:

- Positive expense amounts.
- Non-empty category and description fields.
- Valid date values.

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

By default, the application uses SQLite locally. PostgreSQL is configured through the `DATABASE_URL` environment variable in production.

## Deployment

The application is deployed on Render and uses PostgreSQL as its production database.

- **Live API:** https://expense-tracker-api-8tj2.onrender.com
- **Swagger Documentation:** https://expense-tracker-api-8tj2.onrender.com/docs

## Testing

All five API endpoints have been manually tested using the interactive Swagger documentation.