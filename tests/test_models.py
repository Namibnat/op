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
    CollectionModel,
    BucketCollection,
    ProjectCollection,
    TicketCollection,
    RoutinesCollection,
)


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

    def test_get_all_buckets(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_all_buckets retrieves all bucket item dictionaries.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["bucket"]["b1"] = {"item": "Note 1"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        buckets = bucket_col.get_all_buckets()
        assert "b1" in buckets
        assert buckets["b1"]["item"] == "Note 1"

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
        """Verify create() stores a formatted bucket capture item with date_created.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        bucket_col = BucketCollection()
        bucket_col.create("Read chapter 4")

        assert bucket_col.count_all_buckets() == 1
        items = bucket_col.read_all("bucket")
        item_data = list(items.values())[0]
        assert item_data["item"] == "Read chapter 4"
        assert "date_created" in item_data

    def test_get_bucket_exact_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_bucket returns the item with id injected on exact key match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "550e8400-e29b-41d4-a716-446655440000"
        sample_base_data["bucket"][full_id] = {
            "item": "Target item",
            "date_created": "2026-08-16",
            "status": "fresh",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        result = bucket_col.get_bucket(full_id)
        assert result is not None
        assert result["id"] == full_id
        assert result["item"] == "Target item"

    def test_get_bucket_prefix_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_bucket finds an item by short prefix.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "abcdef12-3456-7890-abcd-ef1234567890"
        sample_base_data["bucket"][full_id] = {
            "item": "Prefix item",
            "date_created": "2026-08-16",
            "status": "fresh",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        result = bucket_col.get_bucket("abcdef12")
        assert result is not None
        assert result["id"] == full_id
        assert result["item"] == "Prefix item"

    def test_get_bucket_not_found(self, isolated_storage_dir: Path):
        """Verify get_bucket returns None when ID prefix does not match any item.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        bucket_col = BucketCollection()
        result = bucket_col.get_bucket("nonexistent-prefix")
        assert result is None

    def test_discard_bucket_success_exact_id(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify discard_bucket deletes the item from database and returns True.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        item_id = "11111111-2222-3333-4444-555555555555"
        sample_base_data["bucket"][item_id] = {"item": "To be deleted"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        success = bucket_col.discard_bucket(item_id)
        assert success is True
        assert bucket_col.count_all_buckets() == 0

        # Check persisted file
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert item_id not in disk_data["bucket"]

    def test_discard_bucket_success_prefix_id(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify discard_bucket deletes the item when passed a prefix ID.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        item_id = "88888888-2222-3333-4444-555555555555"
        sample_base_data["bucket"][item_id] = {"item": "To delete via prefix"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        success = bucket_col.discard_bucket("88888888")
        assert success is True
        assert bucket_col.count_all_buckets() == 0

    def test_discard_bucket_not_found(self, isolated_storage_dir: Path):
        """Verify discard_bucket returns False when item does not exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        bucket_col = BucketCollection()
        success = bucket_col.discard_bucket("nonexistent-id")
        assert success is False


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

    def test_create_project(self, isolated_storage_dir: Path):
        """Verify create() stores project with date_created and returns (project_dict, id).

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        new_project_data = {
            "name": "Build treehouse",
            "spec": "Two-story wooden treehouse",
            "state": "active",
            "done_when": "Roof and ladder complete",
        }
        project, project_id = project_col.create(new_project_data)

        assert isinstance(project_id, str)
        assert len(project_id) == 36
        assert project["name"] == "Build treehouse"
        assert project["spec"] == "Two-story wooden treehouse"
        assert project["done_when"] == "Roof and ladder complete"
        assert "date_created" in project

        # Verify persisted on disk
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert project_id in disk_data["projects"]
        assert disk_data["projects"][project_id]["name"] == "Build treehouse"

    def test_get_all_projects_empty(self, isolated_storage_dir: Path):
        """Verify get_all_projects returns empty dictionary when no projects exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        projects = project_col.get_all_projects()
        assert projects == {}

    def test_get_all_projects_populated(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_all_projects returns populated projects dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"]["p1"] = {"name": "Project 1"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        projects = project_col.get_all_projects()
        assert "p1" in projects
        assert projects["p1"]["name"] == "Project 1"

    def test_get_project_exact_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project returns project with injected id on exact key match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "660e8400-e29b-41d4-a716-446655440000"
        sample_base_data["projects"][full_id] = {
            "name": "Exact Project",
            "spec": "Project spec details",
            "state": "active",
            "done_when": "Everything complete",
            "date_created": "2026-08-17",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        project = project_col.get_project(full_id)
        assert project is not None
        assert project["id"] == full_id
        assert project["name"] == "Exact Project"

    def test_get_project_prefix_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project returns project on prefix match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "770e8400-e29b-41d4-a716-446655440000"
        sample_base_data["projects"][full_id] = {
            "name": "Prefix Project",
            "spec": "Project spec details",
            "state": "not_started",
            "done_when": "Everything complete",
            "date_created": "2026-08-17",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        project = project_col.get_project("770e8400")
        assert project is not None
        assert project["id"] == full_id
        assert project["name"] == "Prefix Project"

    def test_get_project_not_found(self, isolated_storage_dir: Path):
        """Verify get_project returns None when project ID prefix doesn't match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.get_project("nonexistent-prefix") is None

    def test_get_filtered_project_all(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_filtered_project returns all projects when filter is 'all'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"] = {
            "p1": {"name": "P1", "state": "active"},
            "p2": {"name": "P2", "state": "not_started"},
            "p3": {"name": "P3", "state": "done"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        res = project_col.get_filtered_project("all")
        assert len(res) == 3

    def test_get_filtered_project_by_state(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_filtered_project filters by specific state and maps 'new' to 'not_started'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"] = {
            "p1": {"name": "Active 1", "state": "active"},
            "p2": {"name": "New 1", "state": "not_started"},
            "p3": {"name": "Done 1", "state": "done"},
            "p4": {"name": "Archived 1", "state": "archived"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        active = project_col.get_filtered_project("active")
        assert len(active) == 1
        assert "p1" in active

        new_projs = project_col.get_filtered_project("new")
        assert len(new_projs) == 1
        assert "p2" in new_projs

        done_projs = project_col.get_filtered_project("done")
        assert len(done_projs) == 1
        assert "p3" in done_projs

    def test_get_filtered_project_empty(self, isolated_storage_dir: Path):
        """Verify get_filtered_project returns None when no projects exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.get_filtered_project("active") is None


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
