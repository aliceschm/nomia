import typer

from nomia.services.checker import check
from nomia.services.validator import validate
from nomia.output import format_issue, summarize_issues

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
    function_count = sum(len(rule_data.get("functions", {})) for rule_data in rules.values())

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


if __name__ == "__main__":
    app()
