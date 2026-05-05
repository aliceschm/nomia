import typer

from nomia.models import (
    ISSUE_IMPLEMENTATION_REMOVED,
    ISSUE_MISSING_IMPLEMENTATION,
)


def format_issue(issue: dict) -> str:
    issue_type = issue["type"]

    if issue_type == ISSUE_MISSING_IMPLEMENTATION:
        return f"- [{issue_type}] {issue['rule_id']}"

    if issue_type == ISSUE_IMPLEMENTATION_REMOVED:
        return f"- [{issue_type}] {issue['function']} -> {issue['rule_id']}"

    if "function" in issue:
        return f"- [{issue_type}] {issue['function']} -> {issue['rule_id']}"

    return f"- [{issue_type}] {issue['rule_id']}"


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
