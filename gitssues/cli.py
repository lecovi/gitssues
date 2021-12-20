import pickle
from pathlib import Path

import typer
from dotenv import load_dotenv

import gitssues.jira.cli as jira_app
import gitssues.github.cli as github_app
from gitssues.jira import Jira


load_dotenv()
app = typer.Typer()


app.add_typer(jira_app.app, name="jira")
app.add_typer(github_app.app, name="github")


@app.command()
def prepare():
    p = Path("gitssues.cache")
    if p.exists():
        with p.open("rb") as f:
            jira = pickle.load(f)
    else:
        jira = Jira()
        jira.prepare_jira()
        with p.open("wb") as f:
            pickle.dump(jira, f)

    typer.echo(jira)
    typer.echo("Done!")


@app.command()
def clean():
    p = Path("gitssues.cache")
    if p.exists():
        p.unlink()
    else:
        typer.echo("Nothing to do!")


if __name__ == "__main__":
    app()
