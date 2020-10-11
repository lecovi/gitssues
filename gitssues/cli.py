import json
import os
from dataclasses import dataclass

import requests
import yaml
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def dict_to_dataclass(to_dataclass, from_dict):
    for key, value in from_dict.items():
        setattr(to_dataclass, key, value)


def load_config(path="gitssues.yml"):
    with open(path) as f:
        return yaml.full_load(f)


USERNAME = os.getenv("USERNAME")
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
SCHEDULE_NAME = os.getenv("SCHEDULE_NAME")
OPSGENIE_TOKEN = os.getenv("OPSGENIE_TOKEN")


@dataclass
class Project:
    key: str


@dataclass
class Board:
    id: str


@dataclass
class Sprint:
    id: str


@dataclass
class IssueType:
    name: str


@dataclass
class Issue:
    key: str


@dataclass
class Jira:
    issue: Issue = None
    issue_type: IssueType = None
    board: Board = None
    sprint: Sprint = None
    project: Project = None

    def __post_init__(self):
        self.auth = HTTPBasicAuth(USERNAME, JIRA_TOKEN)
        self.config = load_config()
        self._base_url = self.config["JIRA_BASE_URL"]
        self.labels = self.config["labels"]
        self.project = Project(key=self.config["project_key"])
        self.issue_type = IssueType(name=self.config["issue_type"])

    def get_board(self):
        # FIXME: Error management
        response = requests.get(
            f"{self._base_url}/agile/latest/board",
            auth=self.auth,
            params={"projectKeyOrId": self.project.key},
        )
        response_data = response.json()
        board_data = response_data["values"][0]
        project_data = board_data["location"]
        dict_to_dataclass(self.project, project_data)
        self.board = Board(
            id=board_data["id"],
        )
        dict_to_dataclass(Board, board_data)
        return

    def update_project(self):
        # FIXME: Error management
        response = requests.get(
            f"{self._base_url}/agile/latest/board/{self.board.id}/project",
            auth=self.auth,
            params={"projectKeyOrId": self.config["project_key"]},
        )
        response_data = response.json()
        project_data = response_data["values"][0]
        dict_to_dataclass(self.project, project_data)

    def get_issue_type(self):
        # FIXME: Error management
        response = requests.get(
            f"{self._base_url}/api/3/issue/createmeta",
            auth=self.auth,
            params={"projectKeys": self.config["project_key"]},
        )
        response_data = response.json()
        for issuetype in response_data["projects"][0]["issuetypes"]:
            if issuetype["name"] == self.issue_type.name:
                dict_to_dataclass(self.issue_type, issuetype)

    def get_active_sprint(self):
        response = requests.get(
            f"{self._base_url}/agile/latest/board/{self.board.id}/sprint",
            auth=self.auth,
            params={"state": "active"},
        )
        response_data = response.json()
        sprint_data = response_data["values"][0]
        self.sprint = Sprint(id=sprint_data["id"])
        dict_to_dataclass(self.sprint, sprint_data)

    def load_issue(self, title, content):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "update": {},
            "fields": {
                "summary": title,
                "project": {
                    "id": self.project.id,
                },
                "issuetype": {
                    "id": self.issue_type.id,
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
        response = requests.post(
            f"{self._base_url}/api/3/issue",
            auth=self.auth,
            data=json.dumps(payload),
            headers=headers,
        )
        issue_data = response.json()
        self.issue = Issue(key=issue_data["key"])
        dict_to_dataclass(self.issue, response.json())

    def move_issue_to_sprint(self):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        payload = {
            "issues": [
                self.issue.key,
            ]
        }
        response = requests.post(
            f"{self._base_url}/agile/latest/sprint/{self.sprint.id}/issue",
            auth=self.auth,
            data=json.dumps(payload),
            headers=headers,
        )
        return response

    def get_on_call_users(self):
        headers = {
            "Authorization": f"GenieKey {OPSGENIE_TOKEN}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        response = requests.get(
            f"https://api.opsgenie.com/v2/schedules/{SCHEDULE_NAME}/on-calls",
            headers=headers,
            params={"scheduleIdentifierType": "name"},
        )
        response_json = response.json()
        users = response_json["data"]["onCallParticipants"]
        return users

    def get_account_id(self, mail):
        response = requests.get(
            f"{self._base_url}/api/3/user/assignable/search",
            auth=self.auth,
            params={"issueKey": self.issue.key},
        )
        response_data = response.json()
        for user in response_data:
            if user["emailAddress"] == mail:
                return user["accountId"]

    def assign_issue_to_on_call_user(self):
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        user = self.get_on_call_users()[0]
        account_id = self.get_account_id(mail=user["name"])
        payload = {
            "accountId": account_id,
        }
        response = requests.put(
            f"{self._base_url}/api/3/issue/{self.issue.key}/assignee",
            auth=self.auth,
            data=json.dumps(payload),
            headers=headers,
        )
        return response
