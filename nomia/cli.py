from enum import Enum

import typer

from nomia.output import render_check_output
from nomia.services.auditor import audit_untracked
from nomia.services.checker import check
from nomia.services.validator import validate

app = typer.Typer(
    help="Track business rules in Python projects and detect drift between declared rules and implementations."
)


def _handle_cli_error(exc: Exception, code: int = 1) -> None:
    typer.echo(f"Error: {exc}", err=True)
    raise typer.Exit(code=code) from exc


class CheckOutputFormat(str, Enum):
    default = "default"
    compact = "compact"
    detailed = "detailed"
    json = "json"


@app.callback()
def main(
    ctx: typer.Context,
    config: str | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to Nomia config file.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed discovery and import output.",
    ),
) -> None:
    ctx.obj = {
        "config_path": config,
        "verbose": verbose,
    }


@app.command(name="validate")
def validate_cmd(ctx: typer.Context) -> None:
    """
    Validate Nomia rule tracking and refresh the local validation snapshot.
    """
    try:
        state = validate(
            config_path=ctx.obj["config_path"],
            verbose=ctx.obj["verbose"],
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        _handle_cli_error(exc)

    rules = state.get("rules", {})
    rule_count = len(rules)

    function_count = 0
    for rule_data in rules.values():
        functions = rule_data.get("functions", {})
        function_count += len(functions)

    typer.echo(
        f"Validation snapshot created. Rules tracked: {rule_count}, functions tracked: {function_count}"
    )


@app.command(name="check")
def check_cmd(
    ctx: typer.Context,
    format_mode: CheckOutputFormat = typer.Option(
        CheckOutputFormat.default,
        "--format",
        help="Output format: default, compact, detailed, or json.",
    ),
    strict: bool = typer.Option(
        False,
        "--strict",
        help="Exit with code 1 when findings are found. Useful for CI.",
    ),
) -> None:
    """
    Run repository checks and report findings.

    By default, findings are informational and the command exits with code 0
    when execution succeeds. Use --strict to fail when findings are found.
    """
    try:
        issues = check(
            config_path=ctx.obj["config_path"],
            verbose=ctx.obj["verbose"],
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        _handle_cli_error(exc, code=2)

    typer.echo(render_check_output(issues, format_mode.value))
    raise typer.Exit(code=1 if strict and issues else 0)


@app.command(name="audit")
def audit_cmd(ctx: typer.Context) -> None:
    """
    List discovered project functions that are not linked to a Nomia rule.
    """
    try:
        functions = audit_untracked(
            config_path=ctx.obj["config_path"],
            verbose=ctx.obj["verbose"],
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        _handle_cli_error(exc)

    if not functions:
        typer.echo("No untracked functions found.")
        raise typer.Exit(code=0)

    typer.echo(f"Found {len(functions)} untracked functions.")

    for function_name in functions:
        typer.echo(f"- {function_name}")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
