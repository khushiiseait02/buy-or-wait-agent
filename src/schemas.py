import json
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExpenseItem(BaseModel):
    date: str
    amount: float
    category: str = "general"
    essential: bool = True

class IncomeItem(BaseModel):
    date: str
    amount: float

class FinancialContext(BaseModel):
    current_balance: float = Field(description="User current account balance")
    min_required_balance: float = Field(default=0.0, description="Minimum buffer balance required")
    requested_item_price: float = Field(description="Total price of requested purchase")
    confirmed_incomes: List[IncomeItem] = Field(default_factory=list)
    recurring_expenses: List[ExpenseItem] = Field(default_factory=list)
    pending_payments: List[ExpenseItem] = Field(default_factory=list)

class AgentDecision(BaseModel):
    request_id: str
    amount_safe_to_pay: float
    affordability_status: str
    recommended_payment_method: str
    payment_plan: str
    earliest_date_for_full_payment: str
    spending_changes_needed: str
    decision_explanation: str

    def to_csv_dict(self) -> Dict[str, Any]:
        return self.model_dump()
