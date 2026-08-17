"""Planner elements schema"""

from datetime import date
from enum import Enum

from pydantic import BaseModel


class Bucket(BaseModel):
    """Define buckets"""
    item: str
    date_created: date


class ProjectState(str, Enum):
    """Define project state"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"


class Project(BaseModel):
    """Define projects"""
    name: str
    spec: str
    state: ProjectState
    done_when: str
    date_created: date
