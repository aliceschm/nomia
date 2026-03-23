import typer


def log(message: str, verbose: bool = False) -> None:
    if verbose:
        typer.echo(message)