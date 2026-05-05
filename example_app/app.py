from nomia import rule


@rule("commission.default")
def calculate_commission(amount: float) -> float:
    return amount * 0.30


# duplicate reference (same function, different name)

@rule("discount_eligibility")
def calculate_discount(amount: float) -> float:
    return amount * 0.2
