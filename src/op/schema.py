"""Planner elements schema"""

from datetime import date, datetime
from enum import StrEnum
from typing import Any, Self
import uuid

from pydantic import BaseModel, Field, model_validator


class Bucket(BaseModel):
    """Define buckets"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    item: str
    date_created: date


class ProjectState(StrEnum):
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


class TicketState(StrEnum):
    """Ticket states"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Ticket(BaseModel):
    """Define tickets"""
    pk: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    state: TicketState = TicketState.OPEN
    project: str | None = None
    actionable: bool = True
    context: str = ""
    date_created: date= Field(default_factory=date.today)
    date_completed: date | None = None
    time_bound: bool = False
    due_at: datetime | None = None

    @model_validator(mode="after")
    def validate_due_date(self) -> Self:
        if self.due_at is not None:
            self.time_bound = True
        if self.time_bound and self.due_at is None:
            raise ValueError("Time-bound tickets must have a due date")
        return self
