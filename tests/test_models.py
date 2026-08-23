"""Unit tests for collection models in op.models.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import datetime
import json
from pathlib import Path
import pytest

from op.config import BASE_STRUCTURE
from op.schema import Bucket, Project, ProjectState, ProjectResource, Ticket, TicketState
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
        sample_base_data["bucket"]["b1"] = {"item": "Capture idea", "date_created": "2026-08-19"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        model = CollectionModel()
        bucket_data = model.read_all("bucket")
        assert bucket_data == {"b1": {"item": "Capture idea", "date_created": "2026-08-19"}}

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
        """Verify get_all_buckets retrieves all bucket items as Bucket instances.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["bucket"]["b1"] = {"item": "Note 1", "date_created": "2026-08-19"}
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        buckets = bucket_col.get_all_buckets()
        assert buckets is not None
        assert len(buckets) == 1
        assert isinstance(buckets[0], Bucket)
        assert buckets[0].pk == "b1"
        assert buckets[0].item == "Note 1"

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
        sample_base_data["bucket"]["b1"] = {"item": "First idea", "date_created": "2026-08-19"}
        sample_base_data["bucket"]["b2"] = {"item": "Second idea", "date_created": "2026-08-19"}
        sample_base_data["bucket"]["b3"] = {"item": "Third idea", "date_created": "2026-08-19"}
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
        """Verify get_bucket returns the Bucket instance on exact key match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "550e8400-e29b-41d4-a716-446655440000"
        sample_base_data["bucket"][full_id] = {
            "item": "Target item",
            "date_created": "2026-08-16",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        result = bucket_col.get_bucket(full_id)
        assert result is not None
        assert isinstance(result, Bucket)
        assert result.pk == full_id
        assert result.item == "Target item"

    def test_get_bucket_prefix_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_bucket finds an item by short prefix.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        full_id = "abcdef12-3456-7890-abcd-ef1234567890"
        sample_base_data["bucket"][full_id] = {
            "item": "Prefix item",
            "date_created": "2026-08-16",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        bucket_col = BucketCollection()
        result = bucket_col.get_bucket("abcdef12")
        assert result is not None
        assert isinstance(result, Bucket)
        assert result.pk == full_id
        assert result.item == "Prefix item"

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
        sample_base_data["bucket"][item_id] = {"item": "To be deleted", "date_created": "2026-08-19"}
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
        sample_base_data["bucket"][item_id] = {"item": "To delete via prefix", "date_created": "2026-08-19"}
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
            "p1": {"name": "Active Project 1", "spec": "s1", "state": "active", "done_when": "d1", "date_created": "2026-08-19"},
            "p2": {"name": "Paused Project", "spec": "s2", "state": "not_started", "done_when": "d2", "date_created": "2026-08-19"},
            "p3": {"name": "Completed Project", "spec": "s3", "state": "done", "done_when": "d3", "date_created": "2026-08-19"},
            "p4": {"name": "Active Project 2", "spec": "s4", "state": "active", "done_when": "d4", "date_created": "2026-08-19"},
            "p5": {"name": "Archived Project", "spec": "s5", "state": "archived", "done_when": "d5", "date_created": "2026-08-19"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        assert project_col.count_active_projects() == 2

    def test_create_project(self, isolated_storage_dir: Path):
        """Verify create() stores project with date_created and returns Project instance.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        new_project = Project(
            name="Build treehouse",
            spec="Two-story wooden treehouse",
            state=ProjectState.ACTIVE,
            done_when="Roof and ladder complete",
            date_created=datetime.date.today(),
        )
        created = project_col.create(new_project)

        assert isinstance(created, Project)
        assert len(created.pk) == 36
        assert created.name == "Build treehouse"
        assert created.spec == "Two-story wooden treehouse"
        assert created.done_when == "Roof and ladder complete"

        # Verify persisted on disk
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert created.pk in disk_data["projects"]
        assert disk_data["projects"][created.pk]["name"] == "Build treehouse"

    def test_get_all_projects_empty(self, isolated_storage_dir: Path):
        """Verify get_all_projects returns empty list when no projects exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        projects = project_col.get_all_projects()
        assert projects == []

    def test_get_all_projects_populated(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_all_projects returns list of Project instances.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"]["p1"] = {
            "name": "Project 1",
            "spec": "Spec 1",
            "state": "active",
            "done_when": "Done 1",
            "date_created": "2026-08-19",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        projects = project_col.get_all_projects()
        assert len(projects) == 1
        assert isinstance(projects[0], Project)
        assert projects[0].pk == "p1"
        assert projects[0].name == "Project 1"

    def test_get_project_exact_match(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project returns Project on exact key match.

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
        assert isinstance(project, Project)
        assert project.pk == full_id
        assert project.name == "Exact Project"

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
        assert isinstance(project, Project)
        assert project.pk == full_id
        assert project.name == "Prefix Project"

    def test_get_project_not_found(self, isolated_storage_dir: Path):
        """Verify get_project returns None when project ID prefix doesn't match.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.get_project("nonexistent-prefix") is None

    def test_get_filtered_projects_all(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_filtered_projects returns all projects when filter is 'all'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"] = {
            "p1": {"name": "P1", "spec": "s1", "state": "active", "done_when": "d1", "date_created": "2026-08-19"},
            "p2": {"name": "P2", "spec": "s2", "state": "not_started", "done_when": "d2", "date_created": "2026-08-19"},
            "p3": {"name": "P3", "spec": "s3", "state": "done", "done_when": "d3", "date_created": "2026-08-19"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        res = project_col.get_filtered_projects("all")
        assert len(res) == 3

    def test_get_filtered_projects_by_state(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_filtered_projects filters by specific state and maps 'new' to 'not_started'.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"] = {
            "p1": {"name": "Active 1", "spec": "s1", "state": "active", "done_when": "d1", "date_created": "2026-08-19"},
            "p2": {"name": "New 1", "spec": "s2", "state": "not_started", "done_when": "d2", "date_created": "2026-08-19"},
            "p3": {"name": "Done 1", "spec": "s3", "state": "done", "done_when": "d3", "date_created": "2026-08-19"},
            "p4": {"name": "Archived 1", "spec": "s4", "state": "archived", "done_when": "d4", "date_created": "2026-08-19"},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        active = project_col.get_filtered_projects("active")
        assert len(active) == 1
        assert active[0].pk == "p1"

        new_projs = project_col.get_filtered_projects("new")
        assert len(new_projs) == 1
        assert new_projs[0].pk == "p2"

        done_projs = project_col.get_filtered_projects("done")
        assert len(done_projs) == 1
        assert done_projs[0].pk == "p3"

    def test_get_filtered_projects_empty(self, isolated_storage_dir: Path):
        """Verify get_filtered_projects returns empty list when no projects exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.get_filtered_projects("active") == []

    def test_set_project_state_success(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify set_project_state updates state and persists correctly to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "990e8400-e29b-41d4-a716-446655440000"
        sample_base_data["projects"][proj_id] = {
            "name": "State Test Project",
            "spec": "Spec",
            "state": "not_started",
            "done_when": "Done",
            "date_created": "2026-08-18",
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        updated = project_col.set_project_state("990e8400", ProjectState.ACTIVE)
        assert updated is not None
        assert isinstance(updated, Project)
        assert updated.state == ProjectState.ACTIVE

        # Verify disk persistence
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert disk_data["projects"][proj_id]["state"] == "active"

    def test_set_project_state_not_found(self, isolated_storage_dir: Path):
        """Verify set_project_state returns None when project ID is not found.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        assert project_col.set_project_state("missing-id", ProjectState.DONE) is None

    def test_add_project_resource_success(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify add_project_resource attaches resource and persists to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "aa0e8400-e29b-41d4-a716-446655440000"
        sample_base_data["projects"][proj_id] = {
            "name": "Resource Test Project",
            "spec": "Spec",
            "state": "active",
            "done_when": "Done",
            "date_created": "2026-08-19",
            "resources": {},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        new_res = ProjectResource(type="repo", label="Source Repo", location="github.com/Namibnat/op")
        updated = project_col.add_project_resource("aa0e8400", new_res)

        assert updated is not None
        assert isinstance(updated, Project)
        assert len(updated.resources) == 1

        # Check disk persistence
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        proj_resources = disk_data["projects"][proj_id]["resources"]
        assert len(proj_resources) == 1
        res_data = list(proj_resources.values())[0]
        assert res_data["type"] == "repo"
        assert res_data["label"] == "Source Repo"
        assert res_data["location"] == "github.com/Namibnat/op"

    def test_add_project_resource_multiple(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify add_project_resource supports appending multiple distinct resources.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "bb0e8400-e29b-41d4-a716-446655440000"
        sample_base_data["projects"][proj_id] = {
            "name": "Multi Resource Project",
            "spec": "Spec",
            "state": "active",
            "done_when": "Done",
            "date_created": "2026-08-19",
            "resources": {},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        res1 = ProjectResource(type="doc", label="Design Doc", location="docs/design.md")
        res2 = ProjectResource(type="link", label="Figma Mockup", location="https://figma.com/file/123")

        project_col.add_project_resource("bb0e8400", res1)
        updated = project_col.add_project_resource("bb0e8400", res2)

        assert updated is not None
        assert len(updated.resources) == 2

        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert len(disk_data["projects"][proj_id]["resources"]) == 2

    def test_add_project_resource_not_found(self, isolated_storage_dir: Path):
        """Verify add_project_resource returns None when project ID prefix is not found.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        project_col = ProjectCollection()
        res = ProjectResource(type="link", label="Link", location="http://example.com")
        assert project_col.add_project_resource("nonexistent", res) is None

    def test_delete_project_resource_exact_id(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify delete_project_resource removes resource on exact match and persists to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "12345678-aaaa-bbbb-cccc-dddddddddddd"
        res_id = "87654321-1111-2222-3333-444444444444"
        sample_base_data["projects"][proj_id] = {
            "name": "Delete Test Project",
            "spec": "Spec",
            "state": "active",
            "done_when": "Done",
            "date_created": "2026-08-19",
            "resources": {
                res_id: {
                    "type": "doc",
                    "label": "Old Guide",
                    "location": "docs/old.md",
                }
            },
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        success = project_col.delete_project_resource(proj_id, res_id)
        assert success is True

        project = project_col.get_project(proj_id)
        assert project is not None
        assert len(project.resources) == 0

        # Check disk persistence
        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert len(disk_data["projects"][proj_id]["resources"]) == 0

    def test_delete_project_resource_prefix_id(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify delete_project_resource removes resource when passed a short prefix ID.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "23456789-aaaa-bbbb-cccc-dddddddddddd"
        res_id = "98765432-1111-2222-3333-444444444444"
        sample_base_data["projects"][proj_id] = {
            "name": "Delete Prefix Project",
            "spec": "Spec",
            "state": "active",
            "done_when": "Done",
            "date_created": "2026-08-19",
            "resources": {
                res_id: {
                    "type": "link",
                    "label": "Old Link",
                    "location": "https://example.com/old",
                }
            },
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        success = project_col.delete_project_resource("23456789", "98765432")
        assert success is True

        project = project_col.get_project("23456789")
        assert project is not None
        assert len(project.resources) == 0

    def test_delete_project_resource_not_found(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify delete_project_resource returns False when resource ID is missing.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        proj_id = "34567890-aaaa-bbbb-cccc-dddddddddddd"
        sample_base_data["projects"][proj_id] = {
            "name": "No Resource Project",
            "spec": "Spec",
            "state": "active",
            "done_when": "Done",
            "date_created": "2026-08-19",
            "resources": {},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        project_col = ProjectCollection()
        assert project_col.delete_project_resource(proj_id, "nonexistent") is False
        assert project_col.delete_project_resource("nonexistent-proj", "nonexistent") is False


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

    def test_count_active_tickets_populated(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify count_active_tickets returns count of stored tickets.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["tickets"] = {
            "t1": {"title": "Task 1", "state": "open", "project": None, "actionable": True, "context": "", "date_created": "2026-08-22", "date_completed": None, "time_bound": False, "due_at": None},
            "t2": {"title": "Task 2", "state": "in_progress", "project": None, "actionable": True, "context": "", "date_created": "2026-08-22", "date_completed": None, "time_bound": False, "due_at": None},
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        ticket_col = TicketCollection()
        assert ticket_col.count_active_tickets() == 2

    def test_create_ticket_standalone(self, isolated_storage_dir: Path):
        """Verify create() stores standalone ticket to disk with pk excluded in dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        ticket_col = TicketCollection()
        ticket = Ticket(title="Buy electrical tape", context="errands")
        created = ticket_col.create(ticket)

        assert isinstance(created, Ticket)
        assert created.title == "Buy electrical tape"
        assert created.project is None
        assert created.context == "errands"
        assert ticket_col.count_active_tickets() == 1

        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        assert created.pk in disk_data["tickets"]
        assert "pk" not in disk_data["tickets"][created.pk]
        assert disk_data["tickets"][created.pk]["title"] == "Buy electrical tape"

    def test_create_ticket_project_linked(self, isolated_storage_dir: Path):
        """Verify create() stores project-linked ticket with due_at.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        ticket_col = TicketCollection()
        ticket = Ticket(
            title="Solder wiring harness",
            state=TicketState.IN_PROGRESS,
            project="proj-1234",
            actionable=True,
            context="lab",
            time_bound=True,
            due_at=datetime.datetime(2026, 10, 15, 12, 0),
        )
        created = ticket_col.create(ticket)

        assert created.project == "proj-1234"
        assert created.state == TicketState.IN_PROGRESS
        assert created.time_bound is True

        with open(isolated_storage_dir / "planner.json", "r") as f:
            disk_data = json.load(f)
        saved = disk_data["tickets"][created.pk]
        assert saved["project"] == "proj-1234"
        assert saved["due_at"] == "2026-10-15T12:00:00"

    def test_create_ticket_models_none_or_empty(self):
        """Verify create_ticket_models returns None when data is empty or None.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        assert TicketCollection.create_ticket_models({}) is None
        assert TicketCollection.create_ticket_models(None) is None

    def test_create_ticket_models_expands_dict_to_models(self):
        """Verify create_ticket_models expands stored dictionary into Ticket instances.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        data = {
            "t-1111": {
                "title": "Fix bracket",
                "state": "open",
                "project": "proj-abc",
                "actionable": True,
                "context": "workshop",
                "date_created": "2026-08-20",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
            "t-2222": {
                "title": "Buy bolts",
                "state": "in_progress",
                "project": None,
                "actionable": True,
                "context": "hardware",
                "date_created": "2026-08-21",
                "date_completed": None,
                "time_bound": True,
                "due_at": "2026-08-25T17:00:00",
            },
        }
        models = TicketCollection.create_ticket_models(data)
        assert models is not None
        assert len(models) == 2

        t1 = next(m for m in models if m.pk == "t-1111")
        assert t1.title == "Fix bracket"
        assert t1.project == "proj-abc"
        assert t1.state == TicketState.OPEN

        t2 = next(m for m in models if m.pk == "t-2222")
        assert t2.title == "Buy bolts"
        assert t2.project is None
        assert t2.state == TicketState.IN_PROGRESS
        assert t2.time_bound is True

    def test_get_project_tickets_empty(self, isolated_storage_dir: Path):
        """Verify get_project_tickets returns None when tickets container is empty.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        ticket_col = TicketCollection()
        assert ticket_col.get_project_tickets("proj-1234") is None

    def test_get_project_tickets_returns_matching_tickets(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project_tickets returns all tickets matching the project prefix.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["tickets"] = {
            "t-1": {
                "title": "Mount solar rails",
                "state": "open",
                "project": "880e8400-e29b-41d4-a716-446655440000",
                "actionable": True,
                "context": "roof",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
            "t-2": {
                "title": "Wire inverter",
                "state": "in_progress",
                "project": "880e8400-e29b-41d4-a716-446655440000",
                "actionable": True,
                "context": "shed",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
            "t-3": {
                "title": "Paint fence",
                "state": "open",
                "project": "990e8400-0000-0000-0000-000000000000",
                "actionable": True,
                "context": "garden",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        ticket_col = TicketCollection()
        matched = ticket_col.get_project_tickets("880e8400")
        assert matched is not None
        assert len(matched) == 2
        titles = [t.title for t in matched]
        assert "Mount solar rails" in titles
        assert "Wire inverter" in titles

    def test_get_project_tickets_no_matches_returns_empty_list(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project_tickets returns empty list when tickets exist but none match project.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["tickets"] = {
            "t-1": {
                "title": "Paint fence",
                "state": "open",
                "project": "990e8400-0000-0000-0000-000000000000",
                "actionable": True,
                "context": "garden",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        ticket_col = TicketCollection()
        matched = ticket_col.get_project_tickets("880e8400")
        assert matched == []

    def test_get_project_tickets_ignores_standalone_tickets_without_project(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify get_project_tickets safely handles tickets where project is None.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["tickets"] = {
            "t-standalone": {
                "title": "Buy milk",
                "state": "open",
                "project": None,
                "actionable": True,
                "context": "store",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
            "t-proj": {
                "title": "Solar inspection",
                "state": "open",
                "project": "880e8400-e29b-41d4-a716-446655440000",
                "actionable": True,
                "context": "site",
                "date_created": "2026-08-22",
                "date_completed": None,
                "time_bound": False,
                "due_at": None,
            },
        }
        with open(isolated_storage_dir / "planner.json", "w") as f:
            json.dump(sample_base_data, f)

        ticket_col = TicketCollection()
        matched = ticket_col.get_project_tickets("880e8400")
        assert matched is not None
        assert len(matched) == 1
        assert matched[0].title == "Solar inspection"


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
