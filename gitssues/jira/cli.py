from pathlib import Path
import pickle
import random

import typer

from .api import Jira


app = typer.Typer()


@app.command()
def main():
    typer.echo("Hello Jira!")


@app.command()
def new_bug(
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
        jira = pickle.load(f)

    # Get **Active Sprint** from *Board*
    sprint_data = jira.get_active_sprint_data(board_id=jira.board.id)
    jira.parse_sprint_data(sprint_data=sprint_data)

    # FIXME: make this transaction atomic (if something went wrong, delete the issue)
    # Post **Issue** to *Project* backlog
    issue_data = jira.post_issue_to_backlog(title=title, content=content)
    jira.parse_issue_data(issue_data=issue_data)

    # Move **Issue** to *Active Sprint*
    jira.move_issue_to_sprint(issue_key=jira.issue.key, sprint_id=jira.sprint.id)

    # Assign **Issue** to *User*
    # if usermail is not provided, then search in OpsGenie who is on-call
    if on_call:
        users_data = jira.get_on_call_users_data()
        users = jira.parse_on_call_users_data(on_call_users_data=users_data)
        jira.assign_issue_to_user(
            issue_key=jira.issue.key, user_account_id=users[0]["emailAddress"]
        )
    else:
        users_data = jira.get_assignable_users_for_issue_data(issue_key=jira.issue.key)
        user = random.choice(users_data)
        jira.assign_issue_to_user(
            issue_key=jira.issue.key, user_account_id=user["accountId"]
        )

    typer.echo(
        f"Issue {jira.issue.key} created and assigned to {user['emailAddress']}! "
    )


@app.command()
def comment_bug(
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
        jira = pickle.load(f)

    jira.add_comment_to_issue(issue_key=issue_key, comment=comment)
    typer.echo(f"Comment added to Issue {issue_key}! ")


@app.command()
def change_bug_state(
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
        jira = pickle.load(f)

    transitions_data = jira.get_issue_transitions(issue_key=issue_key)
    transition = jira.get_transition(
        transitions_data=transitions_data, transition_name=new_state
    )

    jira.set_issue_transition(issue_key=issue_key, transition=transition)
    typer.echo(f"Issue {issue_key} set to {new_state}! ")


@app.command()
def delete_bug(
    issue_key: str,
):
    jira = None

    # FIXME: this is possible to have it in a context
    p = Path("gitssues.cache")
    if not p.exists():
        typer.echo("Run prepare before!")
        exit(1)

    with p.open("rb") as f:
        jira = pickle.load(f)

    jira.delete_issue(issue_key=issue_key)
    typer.echo(f"Issue {issue_key} deleted!")


@app.command()
def assign_bug(
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
        jira = pickle.load(f)

    # FIXME: check if usermail is valid
    # FIXME: check if usermail is assignable
    user_data = jira.get_user_data(email=usermail)
    jira.assign_issue_to_user(
        issue_key=issue_key, user_account_id=user_data[0]["accountId"]
    )

    typer.echo(f"Issue {issue_key} assigned to {user_data[0]['emailAddress']}!")
