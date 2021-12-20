from pathlib import Path
import pickle

import typer

from gitssues import __version__


app = typer.Typer()
issue = typer.Typer(help="Issues related commands")
app.add_typer(issue, name="issue")

@app.command(help="Shows CLI version")
def version():
    typer.echo(f"Hello GitHub from Gitssues v{__version__}!")


@issue.command(help="Creates a issue in repo")
def new(
    repo: str,
    title: str,
    body: str,
):
    github = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    r = github.create_issue_for_repo(repo=repo, title=title, body=body)
    typer.echo(f"Issue {r['number']} created in {repo}!")


@issue.command(help="Adds a comment to an issue in repo")
def comment(
    repo: str,
    issue_number: int,
    body: str,
):
    github = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    r = github.create_comment_on_issue(repo=repo, issue_number=issue_number, body=body)
    typer.echo(f"Comment created in Issue {issue_number} from {repo}!")


@issue.command(help="Close issue in repo")
def close(
    repo: str,
    issue_number: int,
):
    github = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    github.change_issue_state(repo=repo, issue_number=issue_number, state="closed")
    typer.echo(f"Issue {issue_number} from {repo} Closed!")


@issue.command(help="Open a closed issue in repo")
def reopen(
    repo: str,
    issue_number: int,
):
    github = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    github.change_issue_state(repo=repo, issue_number=issue_number, state="open")
    typer.echo(f"Issue {issue_number} from {repo} Reopen!")