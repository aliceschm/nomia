ISSUE_MISSING_IMPLEMENTATION = "missing_implementation"
ISSUE_NOT_VALIDATED = "not_validated"
ISSUE_CODE_CHANGED = "code_changed"


def missing_implementation_issue(rule_id: str) -> dict:
    return {
        "type": ISSUE_MISSING_IMPLEMENTATION,
        "rule_id": rule_id,
    }


def not_validated_issue(rule_id: str, function: str) -> dict:
    return {
        "type": ISSUE_NOT_VALIDATED,
        "rule_id": rule_id,
        "function": function,
    }


def code_changed_issue(rule_id: str, function: str) -> dict:
    return {
        "type": ISSUE_CODE_CHANGED,
        "rule_id": rule_id,
        "function": function,
    }