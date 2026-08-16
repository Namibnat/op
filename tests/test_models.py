"""Unit tests for collection models in op.models.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import datetime
import json
from pathlib import Path
import pytest

from op.config import BASE_STRUCTURE
from op.models import (
    date_day_string,
    CollectionModel,
    BucketCollection,
    ProjectCollection,
    TicketCollection,
    RoutinesCollection,
)


def test_date_day_string():
    """Verify date_day_string produces ISO YYYY-MM-DD formatted string.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    date_str = date_day_string()
    parsed = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    assert parsed.year == datetime.datetime.now().year


class TestCollectionModelBase:
    """Tests for the base CollectionModel class.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_read_data_returns_full_data_dictionary(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify read_data returns the complete planner database dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        model = CollectionModel()
        data = model.read_data()
        assert isinstance(data, dict)
        for key in BASE_STRUCTURE.keys():
            assert key in data

    def test_read_all_returns_specific_container(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify read_all extracts the specific container dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["bucket"]["b1"] = {"text": "Capture idea"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        model = CollectionModel()
        bucket_data = model.read_all("bucket")
        assert bucket_data == {"b1": {"text": "Capture idea"}}

    def test_read_all_returns_none_for_nonexistent_container(self, isolated_storage_dir: Path):
        """Verify read_all returns None when container key does not exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        model = CollectionModel()
        result = model.read_all("non_existent_key")
        assert result is None


class TestBucketCollection:
    """Tests for BucketCollection model.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_count_all_buckets_empty(self, isolated_storage_dir: Path):
        """Verify count_all_buckets returns 0 when no bucket items exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        bucket_col = BucketCollection()
        assert bucket_col.count_all_buckets() == 0

    def test_count_all_buckets_with_items(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify count_all_buckets accurately counts stored bucket items.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["bucket"]["b1"] = {"text": "First idea"}
        sample_base_data["bucket"]["b2"] = {"text": "Second idea"}
        sample_base_data["bucket"]["b3"] = {"text": "Third idea"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        assert bucket_col.count_all_buckets() == 3

    def test_create_adds_bucket_item(self, isolated_storage_dir: Path):
        """Verify create() stores a formatted bucket capture item with date_created and status fresh.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        bucket_col = BucketCollection()
        bucket_col.create("Read chapter 4")

        assert bucket_col.count_all_buckets() == 1
        items = bucket_col.read_all("bucket")
        item_data = list(items.values())[0]
        assert item_data["item"] == "Read chapter 4"
        assert "date_created" in item_data
        assert item_data["status"] == "fresh"


class TestProjectCollection:
    """Tests for ProjectCollection model.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_count_active_projects_empty(self, isolated_storage_dir: Path):
        """Verify count_active_projects returns 0 on an empty project list.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.count_active_projects() == 0

    def test_count_active_projects_filtering(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify count_active_projects counts only projects with state == 'active'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"] = {
            "p1": {"name": "Active Project 1", "state": "active"},
            "p2": {"name": "Paused Project", "state": "paused"},
            "p3": {"name": "Completed Project", "state": "completed"},
            "p4": {"name": "Active Project 2", "state": "active"},
            "p5": {"name": "Cancelled Project", "state": "cancelled"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        assert project_col.count_active_projects() == 2


class TestTicketCollection:
    """Tests for TicketCollection model.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_count_active_tickets_empty(self, isolated_storage_dir: Path):
        """Verify count_active_tickets returns 0 when no tickets exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        ticket_col = TicketCollection()
        assert ticket_col.count_active_tickets() == 0

    def test_count_active_tickets_filtering(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify count_active_tickets counts only tickets with state == 'active'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["tickets"] = {
            "t1": {"title": "Active Ticket 1", "state": "active"},
            "t2": {"title": "Done Ticket", "state": "done"},
            "t3": {"title": "Active Ticket 2", "state": "active"},
            "t4": {"title": "Cancelled Ticket", "state": "cancelled"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        ticket_col = TicketCollection()
        assert ticket_col.count_active_tickets() == 2


class TestRoutinesCollection:
    """Tests for RoutinesCollection model.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_count_active_habits_empty(self, isolated_storage_dir: Path):
        """Verify count_active_habits returns 0 when no habits/routines exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        routines_col = RoutinesCollection()
        assert routines_col.count_active_habits() == 0

    def test_count_active_habits_filtering(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify count_active_habits counts only routines with state == 'active'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["habits"] = {
            "h1": {"name": "Daily Habit 1", "state": "active"},
            "h2": {"name": "Paused Habit", "state": "paused"},
            "h3": {"name": "Daily Habit 2", "state": "active"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        routines_col = RoutinesCollection()
        assert routines_col.count_active_habits() == 2
