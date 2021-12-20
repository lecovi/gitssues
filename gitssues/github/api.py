import os
from dataclasses import dataclass
from http import HTTPStatus

import requests
from requests.auth import HTTPBasicAuth

from gitssues.helpers import read_config
from .exc import GitHubException


@dataclass
class GitHub:
    repo: str = None

    def __post_init__(self, config_file="gitssues.yml"):
        self._headers = {"Accept": "application/vnd.github.v3+json"}
        self._load_config(path=config_file)
        self._load_auth_credentials()

    def _load_auth_credentials(self):
        """
        Reads GITHUB_USERNAME and GITHUB_TOKEN from environment variables and sets the auth.
        """
        GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
        GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
        self.auth = HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN)

    def _load_config(self, path):
        """
        Loads the configuration file from path.
        """
        self.config = read_config(path=path)
        self._base_url = self.config["GITHUB_BASE_URL"]

    def get_issues_from_repo(self, repo):
        """
        Get the list of issues for a repo. repo is owner/repo string.
        Returns JSON response.

        According to the GitHub API documentation, https://docs.github.com/en/rest/reference/issues#list-repository-issues
        """

        URL = f"{self._base_url}/repos/{repo}/issues"

        response = requests.get(
            url=URL,
            auth=self.auth,
            headers=self._headers,
            )
        
        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Error while getting issues from {repo}: {response.status_code} - {response.text}"
            )
            raise GitHubException(msg)

        return response.json()

    def create_issue_for_repo(self, repo, title, body):
        """
        Create a new issue in a repo. repo is owner/repo string.
        Returns JSON response.

        According to the GitHub API documentation, https://docs.github.com/en/rest/reference/issues#create-an-issue
        """
        URL = f"{self._base_url}/repos/{repo}/issues"

        payload = {
            "title": title,
            "body": body,
        }
        response = requests.post(
            url=URL,
            auth=self.auth,
            headers=self._headers,
            json=payload,
            )
        
        if response.status_code != HTTPStatus.CREATED:
            msg = (
                f"Error while getting issues from {repo}: {response.status_code} - {response.text}"
            )
            raise GitHubException(msg)

        return response.json()
    
    def create_comment_on_issue(self, repo, issue_number, body):
        """
        Create a new issue in a repo. repo is owner/repo string.
        Returns JSON response.

        According to the GitHub API documentation, https://docs.github.com/en/rest/reference/issues#create-an-issue
        """
        URL = f"{self._base_url}/repos/{repo}/issues/{issue_number}/comments"

        payload = {
            "body": body,
        }
        response = requests.post(
            URL,
            auth=self.auth,
            headers=self._headers,
            json=payload,
            )
        
        if response.status_code != HTTPStatus.CREATED:
            msg = (
                f"Error while creating comment on issue {issue_number} of {repo}: {response.status_code} - {response.text}"
            )
            raise GitHubException(msg)

        return response.json()

    def change_issue_state(self, repo, issue_number, state):
        """
        Create a new issue in a repo. repo is owner/repo string.
        Returns JSON response.

        According to the GitHub API documentation, https://docs.github.com/en/rest/reference/issues#create-an-issue
        """
        if state not in ["open", "closed"]:
            raise GitHubException("State must be open or closed")

        URL = f"{self._base_url}/repos/{repo}/issues/{issue_number}"

        payload = {
            "state": state,
        }
        response = requests.patch(
            url=URL,
            auth=self.auth,
            headers=self._headers,
            json=payload,
            )
        
        if response.status_code != HTTPStatus.OK:
            msg = (
                f"Error while changing issue state of {issue_number} of {repo}: {response.status_code} - {response.text}"
            )
            raise GitHubException(msg)

        return response.json()
