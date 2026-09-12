import json
from datetime import datetime, timedelta
from src.schemas import FinancialContext, AgentDecision
from src.config import FORECAST_DAYS

def run_affordability_simulation(
    request_id: str, 
    context: FinancialContext, 
    request_date_str: str = "2026-09-12"
) -> AgentDecision:
    start_date = datetime.strptime(request_date_str, "%Y-%m-%d")
    daily_balances = {}
    current_balance = context.current_balance
    min_floor = context.min_required_balance
    item_price = context.requested_item_price

    for day in range(FORECAST_DAYS):
        curr_date = start_date + timedelta(days=day)
        date_str = curr_date.strftime("%Y-%m-%d")

        for inc in context.confirmed_incomes:
            if inc.date == date_str:
                current_balance += inc.amount

        for exp in context.recurring_expenses:
            if exp.date == date_str and exp.essential:
                current_balance -= exp.amount

        for pend in context.pending_payments:
            if pend.date == date_str:
                current_balance -= pend.amount

        daily_balances[date_str] = current_balance

    can_pay_full_now = all((bal - item_price) >= min_floor for bal in daily_balances.values())

    if can_pay_full_now:
        plan = json.dumps([{"date": request_date_str, "amount": item_price}])
        return AgentDecision(
            request_id=request_id,
            amount_safe_to_pay=item_price,
            affordability_status="Affordable Now",
            recommended_payment_method="Pay in Full",
            payment_plan=plan,
            earliest_date_for_full_payment=request_date_str,
            spending_changes_needed="None",
            decision_explanation=(
                f"Full payment of ${item_price:.2f} leaves balance above the required floor "
                f"of ${min_floor:.2f} across the forecast period."
            )
        )

    earliest_safe_date = "N/A"
    for date_str, bal in daily_balances.items():
        if (bal - item_price) >= min_floor:
            earliest_safe_date = date_str
            break

    amount_safe_today = max(0.0, round(daily_balances[request_date_str] - min_floor, 2))

    if earliest_safe_date != "N/A":
        plan = json.dumps([{"date": earliest_safe_date, "amount": item_price}])
        return AgentDecision(
            request_id=request_id,
            amount_safe_to_pay=amount_safe_today,
            affordability_status="Affordable Later",
            recommended_payment_method="Wait for Full Payment",
            payment_plan=plan,
            earliest_date_for_full_payment=earliest_safe_date,
            spending_changes_needed="None",
            decision_explanation=(
                f"Paying in full today breaches minimum balance floor. Full payment is delayed "
                f"until {earliest_safe_date} following confirmed cash inflows."
            )
        )

    return AgentDecision(
        request_id=request_id,
        amount_safe_to_pay=amount_safe_today,
        affordability_status="Not Affordable",
        recommended_payment_method="Do Not Proceed",
        payment_plan="[]",
        earliest_date_for_full_payment="N/A",
        spending_changes_needed="Reduce discretionary spending and subscriptions.",
        decision_explanation=(
            f"The item price exceeds safe liquidity bounds throughout the 60-day forecast."
        )
    )
