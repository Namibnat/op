"""Planner elements schema"""

from datetime import date
from enum import Enum
import uuid

from pydantic import BaseModel, Field


class Bucket(BaseModel):
    """Define buckets"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item: str
    date_created: date


class ProjectResource(BaseModel):
    type: str
    label: str
    location: str


class ProjectState(str, Enum):
    """Define project state"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"


class Project(BaseModel):
    """Define projects"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    spec: str
    state: ProjectState
    done_when: str
    date_created: date
    resources: dict[str, ProjectResource] = Field(default_factory=dict)
