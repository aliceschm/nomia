import typer

from nomia.output import format_issue, summarize_issues
from nomia.services.auditor import audit_untracked
from nomia.services.checker import check
from nomia.services.validator import validate

app = typer.Typer(help="Nomia CLI")


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
    state = validate(
        config_path=ctx.obj["config_path"],
        verbose=ctx.obj["verbose"],
    )

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
def check_cmd(ctx: typer.Context) -> None:
    issues = check(
        config_path=ctx.obj["config_path"],
        verbose=ctx.obj["verbose"],
    )

    if not issues:
        typer.echo("Nomia is up to date.")
        raise typer.Exit(code=0)

    typer.echo(f"Nomia found {len(issues)} pending items.")

    for line in summarize_issues(issues):
        typer.echo(line)

    typer.echo("")

    for issue in issues:
        typer.echo(format_issue(issue))

    raise typer.Exit(code=1)


@app.command(name="audit")
def audit_cmd(ctx: typer.Context) -> None:
    functions = audit_untracked(
        config_path=ctx.obj["config_path"],
        verbose=ctx.obj["verbose"],
    )

    if not functions:
        typer.echo("No untracked functions found.")
        raise typer.Exit(code=0)

    typer.echo(f"Found {len(functions)} untracked functions.")

    for function_name in functions:
        typer.echo(f"- {function_name}")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()