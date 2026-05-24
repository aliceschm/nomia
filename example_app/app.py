from nomia import rule


@rule("orders_above_credit_limit_must_be_blocked")
def can_approve_order(order_amount: float, available_credit: float) -> bool:
    return order_amount <= available_credit


@rule("high_risk_customers_require_manual_approval")
def requires_manual_approval(customer_risk_level: str) -> bool:
    return customer_risk_level == "high"


@rule("overdue_customers_cannot_receive_new_credit")
def can_offer_new_credit(has_overdue_balance: bool) -> bool:
    return not has_overdue_balance