"""Planner elements schema"""

from datetime import date
from enum import Enum
from typing import Any
import uuid

from pydantic import BaseModel, Field, model_validator


class Bucket(BaseModel):
    """Define buckets"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item: str
    date_created: date


class ProjectState(str, Enum):
    """Define project state"""
    NOT_STARTED = "not_started"
    ACTIVE = "active"
    DONE = "done"
    ARCHIVED = "archived"


class ProjectResource(BaseModel):
    """Project resource"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str
    label: str
    location: str


class Project(BaseModel):
    """Define projects"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    spec: str
    state: ProjectState
    done_when: str
    date_created: date
    resources: dict[str, ProjectResource] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def populate_resources_pks(cls, data: Any) -> Any:
        """Expand <pk>: <resource> on deserialization"""
        if isinstance(data, dict) and "resources" in data and isinstance(data["resources"], dict):
            for res_pk, res_val in data['resources'].items():
                if isinstance(res_val, dict):
                    res_val["pk"] = res_pk
        return data
