import json

import typer

from nomia.models import (
    ISSUE_CODE_CHANGED,
    ISSUE_IMPLEMENTATION_REMOVED,
    ISSUE_MISSING_IMPLEMENTATION,
    ISSUE_NOT_VALIDATED,
    ISSUE_RULE_CONTENT_CHANGED,
    ISSUE_RULE_REMOVED,
)


CHECK_OUTPUT_FORMATS = ("default", "compact", "detailed", "json")

ISSUE_LABELS = {
    ISSUE_CODE_CHANGED: "Code changed",
    ISSUE_IMPLEMENTATION_REMOVED: "Implementation removed",
    ISSUE_MISSING_IMPLEMENTATION: "Missing implementation",
    ISSUE_NOT_VALIDATED: "Pending validation",
    ISSUE_RULE_CONTENT_CHANGED: "Rule content changed",
    ISSUE_RULE_REMOVED: "Rule removed",
}

ISSUE_MEANINGS = {
    ISSUE_CODE_CHANGED: "This implementation changed since the last validated snapshot.",
    ISSUE_IMPLEMENTATION_REMOVED: (
        "This implementation was previously linked to a rule, but was not found."
    ),
    ISSUE_MISSING_IMPLEMENTATION: (
        "This rule is declared, but no implementation was found."
    ),
    ISSUE_NOT_VALIDATED: "This association has not been validated yet.",
    ISSUE_RULE_CONTENT_CHANGED: (
        "This rule changed since the last validated snapshot."
    ),
    ISSUE_RULE_REMOVED: (
        "This rule existed in the validated snapshot, but is no longer declared."
    ),
}


def _issue_label(issue: dict) -> str:
    return ISSUE_LABELS.get(issue["type"], issue["type"].replace("_", " ").title())


def _short_function_name(function_name: str) -> str:
    return function_name.rsplit(".", 1)[-1]


def _issue_subject(issue: dict, *, detailed: bool = False) -> str:
    if "function" in issue:
        function_name = issue["function"]
        return function_name if detailed else _short_function_name(function_name)

    return issue["rule_id"]


def _item_count_text(issues: list[dict]) -> str:
    item_label = "item" if len(issues) == 1 else "items"
    return f"{len(issues)} {item_label}"


def format_issue(issue: dict) -> str:
    issue_type = issue["type"]

    if issue_type == ISSUE_MISSING_IMPLEMENTATION:
        return f"- [{issue_type}] {issue['rule_id']}"

    if issue_type == ISSUE_IMPLEMENTATION_REMOVED:
        return f"- [{issue_type}] {issue['function']} -> {issue['rule_id']}"

    if "function" in issue:
        return f"- [{issue_type}] {issue['function']} -> {issue['rule_id']}"

    if "message" in issue:
        return f"- [{issue_type}] {issue['rule_id']}: {issue['message']}"

    return f"- [{issue_type}] {issue['rule_id']}"


def format_human_issue(issue: dict, *, detailed: bool = False) -> str:
    return f"- {_issue_label(issue)}: {_issue_subject(issue, detailed=detailed)}"


def render_check_output(issues: list[dict], format_mode: str = "default") -> str:
    if format_mode not in CHECK_OUTPUT_FORMATS:
        valid_formats = ", ".join(CHECK_OUTPUT_FORMATS)
        raise ValueError(
            f"Unsupported check output format: {format_mode}. "
            f"Expected one of: {valid_formats}."
        )

    if format_mode == "json":
        return render_check_json(issues)

    if not issues:
        return render_check_success(format_mode)

    if format_mode == "compact":
        return render_check_compact(issues)

    if format_mode == "detailed":
        return render_check_detailed(issues)

    return render_check_default(issues)


def render_check_success(format_mode: str = "default") -> str:
    if format_mode == "compact":
        return "Alignment check passed"

    if format_mode == "detailed":
        return "Alignment check passed\n\nNo items require review."

    return "Nomia is up to date."


def render_check_default(issues: list[dict]) -> str:
    lines = [
        "Alignment check failed",
        "",
        f"{_item_count_text(issues)} require review:",
    ]

    lines.extend(f"  {format_human_issue(issue)}" for issue in issues)
    lines.extend(
        [
            "",
            "Next step:",
            "  Review changes and run `nomia validate`.",
        ]
    )

    return "\n".join(lines)


def render_check_compact(issues: list[dict]) -> str:
    lines = [f"Alignment check failed: {_item_count_text(issues)} require review", ""]
    lines.extend(format_human_issue(issue) for issue in issues)
    return "\n".join(lines)


def render_check_detailed(issues: list[dict]) -> str:
    lines = ["Alignment check failed"]

    for issue in issues:
        issue_type = issue["type"]
        lines.extend(["", _issue_label(issue)])

        if "function" in issue:
            lines.append(f"  Function: {_issue_subject(issue, detailed=True)}")

        lines.append(f"  Rule: {issue['rule_id']}")
        meaning = ISSUE_MEANINGS.get(issue_type, "This item requires review.")
        lines.append(f"  Meaning: {meaning}")

    lines.extend(
        [
            "",
            "Next step:",
            "  Review the changes and run `nomia validate` after confirming the alignment.",
        ]
    )

    return "\n".join(lines)


def render_check_json(issues: list[dict]) -> str:
    payload = {
        "status": "failed" if issues else "passed",
        "issue_count": len(issues),
        "issues": [_json_issue(issue) for issue in issues],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False)


def _json_issue(issue: dict) -> dict:
    rendered = {
        "type": issue["type"],
        "rule_id": issue["rule_id"],
    }

    if "function" in issue:
        rendered["function"] = issue["function"]

    if "message" in issue:
        rendered["message"] = issue["message"]

    return rendered


def log(message: str, verbose: bool = False) -> None:
    if verbose:
        typer.echo(message)


def summarize_issues(issues: list[dict]) -> list[str]:
    counts: dict[str, int] = {}

    for issue in issues:
        issue_type = issue["type"]
        counts[issue_type] = counts.get(issue_type, 0) + 1

    lines: list[str] = []

    for issue_type in sorted(counts):
        lines.append(f"- {issue_type}: {counts[issue_type]}")

    return lines
