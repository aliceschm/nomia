import typer

from nomia.services.checker import check
from nomia.services.validator import validate

app = typer.Typer(help="Nomia CLI")


@app.command(name="validate")
def validate_cmd(project_root: str = "example_app") -> None:
    state = validate(project_root)
    typer.echo(f"Validation snapshot created. Rules tracked: {len(state['rules'])}")


@app.command(name="check")
def check_cmd(project_root: str = "example_app") -> None:
    issues = check(project_root)

    if not issues:
        typer.echo("Nomia is up to date.")
        raise typer.Exit(code=0)

    typer.echo("Nomia found pending items:")
    for issue in issues:
        typer.echo(f"- [{issue['type']}] {issue['function']} -> {issue['rule_id']}")

    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()