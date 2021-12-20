from pathlib import Path
import pickle
import random

import typer

from gitssues import __version__


app = typer.Typer()
bug = typer.Typer(help="Bug related commands")
app.add_typer(bug, name="bug")

@app.command(help="Shows CLI version")
def version():
    typer.echo(f"Hello Jira from Gitssues v{__version__}!")


@bug.command(help="Creates a bug in active sprint and assignes it to a user")
def new(
    title: str,
    content: str,
    on_call: bool = typer.Option(
        False, help="Get who's on-call from OpsGenie Schedule."
    ),
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    jira.new_issue(title=title, content=content, on_call=on_call)

    typer.echo(
        f"Issue {jira.issue.key} created and assigned! "
    )


@bug.command(help="Add comment to an issue")
def comment(
    issue_key: str,
    comment: str,
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    jira.add_comment_to_issue(issue_key=issue_key, comment=comment)
    typer.echo(f"Comment added to Issue {issue_key}! ")


@bug.command(help="Set a new state for an issue")
def transition(
    issue_key: str,
    new_state: str,
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    transitions_data = jira.get_issue_transitions(issue_key=issue_key)
    transition = jira.get_transition(
        transitions_data=transitions_data, transition_name=new_state
    )

    jira.set_issue_transition(issue_key=issue_key, transition=transition)
    typer.echo(f"Issue {issue_key} set to {new_state}! ")


@bug.command(help="Deletes an issue")
def delete(
    issue_key: str,
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    jira.delete_issue(issue_key=issue_key)
    typer.echo(f"Issue {issue_key} deleted!")


@bug.command(help="Assigns an issue to a user")
def assign(
    issue_key: str,
    usermail: str,
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        gitssues = pickle.load(f)
        github = gitssues["github"]
        jira = gitssues["jira"]

    # FIXME: check if usermail is valid
    # FIXME: check if usermail is assignable
    user_data = jira.get_user_data(email=usermail)
    jira.assign_issue_to_user(
        issue_key=issue_key, user_account_id=user_data[0]["accountId"]
    )

    typer.echo(f"Issue {issue_key} assigned to {user_data[0]['emailAddress']}!")
