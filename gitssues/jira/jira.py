"""
This module contains the Jira abstractions and helper classes.
"""
from abc import ABC
from dataclasses import dataclass

from gitssues.helpers import dict_to_dataclass


class BaseJira:
    def update_from_dict(self, data):
        """
        Updates the object with the data from a dictionary.
        """
        dict_to_dataclass(self, data)


@dataclass
class Project(BaseJira):
    key: str = None


@dataclass
class Board(BaseJira):
    id: str = None


@dataclass
class Sprint(BaseJira):
    id: str = None


@dataclass
class IssueType(BaseJira):
    name: str = None


@dataclass
class Issue(BaseJira):
    key: str = None
