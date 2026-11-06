from fastapi import FastAPI, Depends, status, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db, Base, engine
from schemas import ExpenseCreate, ExpenseResponse

Base.metadata.create_all(bind=engine)

from sqlalchemy import func
from datetime import date

from schemas import ExpenseCreate, ExpenseResponse, UserCreate, UserResponse
from security import hash_password

from security import hash_password, create_access_token, verify_password

import jwt

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from security import SECRET_KEY, ALGORITHM
app = FastAPI()
bearer_scheme = HTTPBearer()
@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    new_user = models.User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login")
def login_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if not existing_user or not verify_password(
        user.password,
        existing_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        {"sub": str(existing_user.id)}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = int(payload.get("sub"))

    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user

@app.post(
    "/expenses",
    status_code=status.HTTP_201_CREATED,
    response_model=ExpenseResponse
)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    new_expense = models.Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date,
        user_id=current_user.id #user id comes from the verified token, not the request body(prevent's users to choose another person's id)
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)

    return new_expense

@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(db: Session = Depends(get_db),
 current_user: models.User = Depends(get_current_user)):
    expenses = db.query(models.Expense).filter(models.Expense.user_id == current_user.id).all()

    return expenses

@app.get("/expenses/category/{category}", response_model=list[ExpenseResponse])
def get_expenses_by_category(
    category: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expenses = db.query(models.Expense).filter(
    models.Expense.category == category,
    models.Expense.user_id == current_user.id
).all()

    return expenses


@app.get("/expenses/summary")
def get_monthly_summary(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
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
    models.Expense.date < end_date,
    models.Expense.user_id == current_user.id
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
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    expense = db.query(models.Expense).filter(
    models.Expense.id == expense_id,
    models.Expense.user_id == current_user.id
).first()

    if expense is None:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    db.delete(expense)
    db.commit()

    return {"message": "Expense deleted successfully"}