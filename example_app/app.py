from nomia import rule


@rule("commission.default")
def calculate_commission(amount: float) -> float:
    return amount * 0.30


@rule("comission.bonus")
def calculate_bonis(amount: float) -> float:
    return amount * 0.2
