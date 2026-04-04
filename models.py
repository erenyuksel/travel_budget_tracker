from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from db import Base


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    trip_name = Column(String(100), nullable=False, default="My Trip")
    total_budget = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="CHF")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    categories = relationship(
        "CategoryAllocation",
        back_populates="budget",
        cascade="all, delete-orphan"
    )
    expenses = relationship(
        "Expense",
        back_populates="budget",
        cascade="all, delete-orphan"
    )


class CategoryAllocation(Base):
    __tablename__ = "category_allocations"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(50), nullable=False)
    percentage = Column(Float, nullable=False)
    allocated_amount = Column(Float, nullable=False)

    budget = relationship("Budget", back_populates="categories")
    expenses = relationship("Expense", back_populates="category")

    __table_args__ = (
        CheckConstraint("percentage >= 0 AND percentage <= 100", name="check_percentage_range"),
    )


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    budget_id = Column(Integer, ForeignKey("budgets.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(Integer, ForeignKey("category_allocations.id", ondelete="RESTRICT"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    expense_date = Column(Date, nullable=False, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)

    budget = relationship("Budget", back_populates="expenses")
    category = relationship("CategoryAllocation", back_populates="expenses")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_amount_positive"),
    )
