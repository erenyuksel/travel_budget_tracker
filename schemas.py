# It contains simple Pydantic models for input validation.

from datetime import date, datetime
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str
    percentage: float = Field(..., ge=0, le=100)


class BudgetCreate(BaseModel):
    trip_name: str = "My Trip"
    total_budget: float = Field(..., gt=0)
    currency: str = "CHF"
    categories: list[CategoryCreate]


class ExpenseCreate(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0)
    description: str | None = None
    expense_date: date


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: float | None = Field(default=None, gt=0)
    description: str | None = None
    expense_date: date | None = None


class BudgetSummary(BaseModel):
    total_budget: float
    total_spent: float
    remaining_budget: float


class CategoryOverview(BaseModel):
    id: int
    name: str
    percentage: float
    allocated_amount: float
    spent_amount: float
    remaining_amount: float


class ExpenseOut(BaseModel):
    id: int
    amount: float
    description: str | None = None
    expense_date: date
    category_id: int


class DashboardOut(BaseModel):
    budget_id: int
    trip_name: str
    currency: str
    created_at: datetime
    summary: BudgetSummary
    categories: list[CategoryOverview]


class CategoryDetailsOut(BaseModel):
    category: CategoryOverview
    expenses: list[ExpenseOut]
