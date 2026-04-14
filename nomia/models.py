ISSUE_MISSING_IMPLEMENTATION = "missing_implementation"
ISSUE_NOT_VALIDATED = "not_validated"
ISSUE_CODE_CHANGED = "code_changed"
ISSUE_IMPLEMENTATION_REMOVED = "implementation_removed"
STATE_RULES_KEY = "rules"
STATE_FUNCTIONS_KEY = "functions"
STATE_CODE_HASH_KEY = "code_hash"
STATE_SCHEMA_VERSION_KEY = "schema_version"
CURRENT_SCHEMA_VERSION = 1


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

def implementation_removed_issue(rule_id: str, function: str) -> dict:
    return {
        "type": ISSUE_IMPLEMENTATION_REMOVED,
        "rule_id": rule_id,
        "function": function,
    }

def create_empty_state() -> dict:
    return {
        STATE_SCHEMA_VERSION_KEY: CURRENT_SCHEMA_VERSION,
        STATE_RULES_KEY: {},
    }


def add_function_to_state(
    state: dict,
    rule_id: str,
    function_name: str,
    code_hash: str,
) -> None:
    state.setdefault(STATE_RULES_KEY, {})
    state[STATE_RULES_KEY].setdefault(rule_id, {STATE_FUNCTIONS_KEY: {}})
    state[STATE_RULES_KEY][rule_id][STATE_FUNCTIONS_KEY][function_name] = {
        STATE_CODE_HASH_KEY: code_hash
    }
