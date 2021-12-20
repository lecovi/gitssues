"""
This module contains the main Jira API class.
"""
from dataclasses import dataclass, field
from http import HTTPStatus
import os

import requests

from gitssues.helpers import read_config
from .exc import JiraException, OpsGenieException
from .jira import Project, Board, Sprint, IssueType, Issue


USERNAME = os.getenv("USERNAME")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
OPSGENIE_SCHEDULE_NAME = os.getenv("OPSGENIE_SCHEDULE_NAME")
OPSGENIE_TOKEN = os.getenv("OPSGENIE_TOKEN")


@dataclass
class Jira:
    board: Board = field(default_factory=Board)
    project: Project = field(default_factory=Project)
    issue_types: list[IssueType] = field(default_factory=list)
    default_issue_type: IssueType = field(default_factory=IssueType)
    sprint: Sprint = field(default_factory=Sprint)
    issue: Issue = field(default_factory=Issue)

    def __post_init__(self, config_file="gitssues.yml"):
        self._load_config(path=config_file)
        self._load_auth_credentials()

    def _load_auth_credentials(self):
        """
        Reads USERNAME and JIRA_TOKEN from environment variables and sets the auth.
        """
        USERNAME = os.getenv("USERNAME")
        JIRA_TOKEN = os.getenv("JIRA_TOKEN")
        self.auth = requests.auth.HTTPBasicAuth(USERNAME, JIRA_TOKEN)

    def _load_config(self, path):
        """
        Loads the configuration file from path.
        """
        self.config = read_config(path=path)
        self._base_url = self.config["JIRA_BASE_URL"]
        self._scd_api_version = self.config["JIRA_SCD_API_VERSION"]
        self._cpd_api_version = self.config["JIRA_CPD_API_VERSION"]
        self.labels = self.config["labels"]

    def get_board_data(self, project_key, version=None):
        """
        Returns the board data from Jira API using project_key.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-agile-1-0-board-boardid-get
        """
        if version is None:
            version = self._scd_api_version

        URL = f"{self._base_url}/agile/{version}/board"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"projectKeyOrId": project_key},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting board: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def get_project_data(self, board_id, project_key, version=None):
        """
        Returns the project data from Jira API using project_key and BoardId.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/#api-agile-1-0-board-boardid-project-get
        """
        if version is None:
            version = self._scd_api_version

        URL = f"{self._base_url}/agile/{version}/board/{board_id}/project"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"projectKeyOrId": project_key},
        )

        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Error while getting project: {response.status_code} - {response.text}"
            )
            raise JiraException(msg)

        return response.json()

    def get_issue_types_data(self, project_key, version=None):
        """
        Returns the issue type from Jira API using project_key.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-createmeta-get
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/createmeta"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"projectKeys": project_key},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting issue type info: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def prepare_jira(self):
        """
        Prepares the Jira object for further usage.
        """
        # TODO: add logging
        board_data = self.get_board_data(project_key=self.config["project_key"])
        self.board.update_from_dict(board_data["values"][0])

        project_data = self.get_project_data(
            board_id=self.board.id, project_key=self.config["project_key"]
        )
        self.project.update_from_dict(project_data["values"][0])

        issue_types_data = self.get_issue_types_data(
            project_key=self.config["project_key"]
        )
        for issue_type_data in issue_types_data["projects"][0]["issuetypes"]:
            issue_type = IssueType()
            issue_type.update_from_dict(issue_type_data)
            if issue_type.name == self.config["default_issue_type"]:
                self.default_issue_type = issue_type
            self.issue_types.append(issue_type)

    def get_active_sprint_data(self, board_id, version=None):
        """
        Returns the active sprint and updates values of Sprint object into the Jira object.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-agile-1-0-sprint-sprintid-get
        """
        if version is None:
            version = self._scd_api_version

        URL = f"{self._base_url}/agile/{version}/board/{board_id}/sprint"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"state": "active"},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting active sprint: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def parse_sprint_data(self, sprint_data):
        """
        Parses the sprint data and updates values of Sprint object into the Jira object.
        """
        self.sprint.update_from_dict(sprint_data["values"][0])

    def post_issue_to_backlog(self, title, content, version=None):
        """
        Post an issue to current project. Returns response object.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-post
        """
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "update": {},
            "fields": {
                "summary": title,
                "project": {
                    "id": self.project.id,
                },
                "issuetype": {
                    "id": self.default_issue_type.id,
                },
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": content,
                                    "type": "text",
                                }
                            ],
                        }
                    ],
                },
                "labels": self.labels,
            },
        }

        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue"

        response = requests.post(
            url=URL,
            auth=self.auth,
            json=payload,
            headers=headers,
        )

        if response.status_code != HTTPStatus.CREATED:
            msg = f"Error while posting issue: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def parse_issue_data(self, issue_data):
        """
        Parses the issue data and updates values of Issue object into the Jira object.
        """
        self.issue = Issue()
        self.issue.update_from_dict(issue_data)

    def get_issue_data(self, issue_key, version=None):
        """
        Returns the issue data from Jira API using project_key.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-get
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}"

        response = requests.get(
            url=URL,
            auth=self.auth,
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting issue: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def delete_issue(self, issue_key, version=None):
        """
        Deletes the issue data from Jira API using issue_key.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-delete
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}"

        response = requests.delete(
            url=URL,
            auth=self.auth,
        )

        if response.status_code != HTTPStatus.NO_CONTENT:
            msg = f"Error while getting issue: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return

    def add_comment_to_issue(self, issue_key, comment, version=None):
        """
        Adds a comment to the issue. Returns response object.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/#api-rest-api-3-issue-issueidorkey-comment-post
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}/comment"

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"text": comment, "type": "text"}],
                    }
                ],
            }
        }
        response = requests.post(
            url=URL,
            auth=self.auth,
            json=payload,
            headers=headers,
        )

        if response.status_code != HTTPStatus.CREATED:
            msg = (
                f"Error while setting comment: {response.status_code} - {response.text}"
            )
            raise JiraException(msg)

        return response.json()

    def get_issue_transitions(self, issue_key, version=None):
        """
        Get issue possible Transitions. Returns response object.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-get
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}/transitions"

        response = requests.get(
            url=URL,
            auth=self.auth,
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting transitions: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def get_transition(self, transitions_data, transition_name):
        """
        Parses the transitions data and returns values of Transition object.
        """
        transition = None
        for item in transitions_data["transitions"]:
            if item["name"] == transition_name:
                transition = item
                return transition

    def set_issue_transition(self, issue_key, transition, version=None):
        """
        Change issue state. Returns None.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-transitions-post
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}/transitions"

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {"transition": {"id": transition["id"]}}
        response = requests.post(
            url=URL,
            auth=self.auth,
            json=payload,
            headers=headers,
        )

        if response.status_code != HTTPStatus.NO_CONTENT:
            msg = f"Error while setting transition: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return

    def move_issue_to_sprint(self, issue_key, sprint_id, version=None):
        """
        Moves issue to current sprint. Returns None.

        According to the JIRA API documentation, https://developer.atlassian.com/cloud/jira/software/rest/api-group-sprint/#api-agile-1-0-sprint-sprintid-issue-post
        """
        if version is None:
            version = self._scd_api_version

        URL = f"{self._base_url}/agile/{version}/sprint/{sprint_id}/issue"

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "issues": [
                issue_key,
            ]
        }
        response = requests.post(
            url=URL,
            auth=self.auth,
            json=payload,
            headers=headers,
        )

        if response.status_code != HTTPStatus.NO_CONTENT:
            msg = f"Error while moving issue to sprint: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return

    def get_on_call_users_data(self):
        """
        Returns a list of users on call.

        According to the OpsGenie API documentation, https://docs.opsgenie.com/docs/who-is-on-call-api#get-on-calls
        """
        headers = {
            "Authorization": f"GenieKey {OPSGENIE_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.get(
            f"https://api.opsgenie.com/v2/schedules/{OPSGENIE_SCHEDULE_NAME}/on-calls",
            headers=headers,
            params={"scheduleIdentifierType": "name"},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting on-call users: {response.status_code} - {response.text}"
            raise OpsGenieException(msg)

        return response.json()

    def parse_on_call_users_data(self, on_call_users_data):
        """
        Parses the on call users data and returns a list of users.
        """
        return on_call_users_data["data"]["onCalls"]

    def get_assignable_users_for_issue_data(self, issue_key, version=None):
        """
        Returns the account id of the user.

        According to the Jira API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-assignable-search-get
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/user/assignable/search"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"issueKey": issue_key},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting assignable users: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()

    def assign_issue_to_user(self, issue_key, user_account_id, version=None):
        """
        Assigns issue to user. Returns None.

        According to the Jira API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/#api-rest-api-3-issue-issueidorkey-assignee-put
        """
        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/issue/{issue_key}/assignee"

        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "accountId": user_account_id,
        }
        response = requests.put(
            url=URL,
            auth=self.auth,
            json=payload,
            headers=headers,
        )

        if response.status_code != HTTPStatus.NO_CONTENT:
            msg = f"Error while assigning issue to user: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return

    def get_user_data(self, email, version=None):
        """
        Get user data from email address. Returns response object.
        According to the Jira API documentation, https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search/#api-rest-api-3-user-search-get
        """

        if version is None:
            version = self._cpd_api_version

        URL = f"{self._base_url}/api/{version}/user/search"

        response = requests.get(
            url=URL,
            auth=self.auth,
            params={"query": email},
        )

        if response.status_code != HTTPStatus.OK:
            msg = f"Error while getting users: {response.status_code} - {response.text}"
            raise JiraException(msg)

        return response.json()
