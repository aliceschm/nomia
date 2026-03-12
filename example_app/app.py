from nomia import rule


@rule("commission.default")
def calculate_commission(amount: float) -> float:
    return amount * 0.25