from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import ExpenseCreate, ExpenseResponse
app = FastAPI()

from sqlalchemy import func
from datetime import date

@app.post(
    "/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseResponse
)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db)
):
    new_expense = models.Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db)):
    expenses = db.query(models.Expense).all()

    return expenses

@app.get("/expenses/category/{category}", response_model=list[ExpenseResponse])
def get_expenses_by_category(
    category: str,
    db: Session = Depends(get_db)
):
    expenses = db.query(models.Expense).filter(
        models.Expense.category == category
    ).all()

    return expenses


@app.get("/expenses/summary")
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    summary = db.query(
        models.Expense.category,
        func.sum(models.Expense.amount).label("total")
    ).filter(
        models.Expense.date >= start_date,
        models.Expense.date < end_date
    ).group_by(
        models.Expense.category
    ).all()

    return {
        category: total
        for category, total in summary
    }


@app.delete("/expenses/{expense_id}")
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    expense = db.query(models.Expense).filter(
        models.Expense.id == expense_id
    ).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}