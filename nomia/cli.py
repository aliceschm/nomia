import typer
from pathlib import Path

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
) -> None:
    ctx.obj = {"config": config}


@app.command(name="validate")
def validate_cmd(ctx: typer.Context) -> None:
    config_path = ctx.obj.get("config")
    state = validate(config_path)
    typer.echo(f"Validation snapshot created. Rules tracked: {len(state['rules'])}")


@app.command(name="check")
def check_cmd(ctx: typer.Context) -> None:
    config_path = ctx.obj.get("config")
    issues = check(config_path)

    if not issues:
        typer.echo("Nomia is up to date.")
        raise typer.Exit(code=0)

    typer.echo("Nomia found pending items:")
    for issue in issues:
        typer.echo(f"- [{issue['type']}] {issue['function']} -> {issue['rule_id']}")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()