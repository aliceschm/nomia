from nomia import rule

@rule("discount_eligibility")
def validate_discount_eligibility(customer):
    return customer.is_adimplente


