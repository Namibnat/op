"""Unit tests for Pydantic domain schemas in op.schema.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import datetime
import pytest
from pydantic import ValidationError

from op.schema import Bucket, ProjectState, Project


class TestBucketSchema:
    """Tests for the Bucket schema.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_bucket_valid(self):
        """Verify Bucket parses string dates and date objects.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        b = Bucket(item="Buy groceries", date_created=datetime.date(2026, 8, 17))
        assert b.item == "Buy groceries"
        assert b.date_created == datetime.date(2026, 8, 17)

        # Parsing from ISO date string
        b_from_str = Bucket.model_validate({"item": "Buy groceries", "date_created": "2026-08-17"})
        assert b_from_str.date_created == datetime.date(2026, 8, 17)

    def test_bucket_json_serialization(self):
        """Verify Bucket serializes date_created to ISO string in json mode.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        b = Bucket(pk="custom-id", item="Idea", date_created=datetime.date(2026, 8, 17))
        data = b.model_dump(mode="json")
        assert data == {"pk": "custom-id", "item": "Idea", "date_created": "2026-08-17"}

        data_no_pk = b.model_dump(mode="json", exclude={"pk"})
        assert data_no_pk == {"item": "Idea", "date_created": "2026-08-17"}


class TestProjectSchema:
    """Tests for Project schema and ProjectState enum.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_project_state_enum_values(self):
        """Verify ProjectState defines expected lifecycle states.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        assert ProjectState.NOT_STARTED == "not_started"
        assert ProjectState.ACTIVE == "active"
        assert ProjectState.DONE == "done"
        assert ProjectState.ARCHIVED == "archived"

    def test_project_valid(self):
        """Verify Project parses valid fields into structured types.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        p = Project.model_validate(
            {
                "name": "Build app",
                "spec": "CLI tool",
                "state": "active",
                "done_when": "Tests pass",
                "date_created": "2026-08-17",
            }
        )
        assert p.name == "Build app"
        assert p.state == ProjectState.ACTIVE
        assert p.date_created == datetime.date(2026, 8, 17)

    def test_project_invalid_state_raises_validation_error(self):
        """Verify invalid project state raises ValidationError.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        with pytest.raises(ValidationError):
            Project.model_validate(
                {
                    "name": "Build app",
                    "spec": "CLI tool",
                    "state": "unknown_state",
                    "done_when": "Tests pass",
                    "date_created": "2026-08-17",
                }
            )

    def test_project_with_resources(self):
        """Verify Project parses embedded resources dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        p = Project.model_validate(
            {
                "name": "App",
                "spec": "Spec",
                "state": "active",
                "done_when": "Done",
                "date_created": "2026-08-17",
                "resources": {
                    "r1": {
                        "type": "repo",
                        "label": "GitHub",
                        "location": "https://github.com/Namibnat/op",
                    }
                },
            }
        )
        assert len(p.resources) == 1
        assert "r1" in p.resources
        assert p.resources["r1"].type == "repo"
        assert p.resources["r1"].label == "GitHub"
        assert p.resources["r1"].location == "https://github.com/Namibnat/op"


class TestProjectResourceSchema:
    """Tests for ProjectResource schema.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_resource_valid_with_default_pk(self):
        """Verify ProjectResource generates UUID pk by default.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import ProjectResource
        res = ProjectResource(type="doc", label="Design Spec", location="docs/spec.md")
        assert len(res.pk) == 36
        assert res.type == "doc"
        assert res.label == "Design Spec"
        assert res.location == "docs/spec.md"

    def test_resource_custom_pk(self):
        """Verify ProjectResource accepts explicit pk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import ProjectResource
        res = ProjectResource(pk="res-123", type="link", label="Figma", location="https://figma.com")
        assert res.pk == "res-123"
        assert res.type == "link"
        assert res.label == "Figma"
        assert res.location == "https://figma.com"


class TestTicketSchema:
    """Tests for Ticket schema and TicketState enum.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_ticket_state_enum_values(self):
        """Verify TicketState defines expected lifecycle states.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import TicketState
        assert TicketState.OPEN == "open"
        assert TicketState.IN_PROGRESS == "in_progress"
        assert TicketState.DONE == "done"
        assert TicketState.CANCELLED == "cancelled"

    def test_ticket_defaults_standalone(self):
        """Verify Ticket initializes valid standalone defaults.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import Ticket, TicketState
        t = Ticket(title="Call electrician")
        assert len(t.pk) == 36
        assert t.title == "Call electrician"
        assert t.state == TicketState.OPEN
        assert t.project is None
        assert t.actionable is True
        assert t.context == ""
        assert t.date_created == datetime.date.today()
        assert t.date_completed is None
        assert t.time_bound is False
        assert t.due_at is None

    def test_ticket_explicit_project_and_time_bound(self):
        """Verify Ticket accepts project linkage and parses due_at datetime.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import Ticket, TicketState
        t = Ticket.model_validate(
            {
                "pk": "t1-uuid",
                "title": "Buy wire connectors",
                "state": "in_progress",
                "project": "proj-123",
                "actionable": True,
                "context": "hardware store",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": True,
                "due_at": "2026-10-12 14:30",
            }
        )
        assert t.pk == "t1-uuid"
        assert t.title == "Buy wire connectors"
        assert t.state == TicketState.IN_PROGRESS
        assert t.project == "proj-123"
        assert t.context == "hardware store"
        assert t.due_at == datetime.datetime(2026, 10, 12, 14, 30)
        assert t.time_bound is True

    def test_ticket_due_at_auto_infers_time_bound(self):
        """Verify setting due_at automatically sets time_bound to True.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import Ticket
        t = Ticket(title="Tax return", due_at=datetime.datetime(2026, 10, 15, 0, 0))
        assert t.time_bound is True

    def test_ticket_time_bound_without_due_at_raises_error(self):
        """Verify time_bound=True without due_at raises ValueError.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import Ticket
        with pytest.raises(ValidationError, match="Time-bound tickets must have a due date"):
            Ticket(title="Must do today", time_bound=True, due_at=None)

    def test_ticket_json_serialization(self):
        """Verify Ticket serializes properly with and without pk exclusion.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        from op.schema import Ticket
        t = Ticket(pk="custom-ticket-pk", title="Write tests")
        dumped_all = t.model_dump(mode="json")
        assert dumped_all["pk"] == "custom-ticket-pk"
        assert dumped_all["title"] == "Write tests"

        dumped_no_pk = t.model_dump(mode="json", exclude={"pk"})
        assert "pk" not in dumped_no_pk
        assert dumped_no_pk["title"] == "Write tests"
