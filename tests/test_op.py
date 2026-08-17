"""High-level integration and CLI entrypoint smoke tests.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import datetime
import json
from pathlib import Path
import pytest

import op
from op.op import (
    date_string,
    get_dashboard_data,
    add_new_bucket_item,
    list_bucket_items,
    show_bucket_item_by_id,
    discard_bucket_item_by_id,
    create_project_by_id,
)
from op.models import BucketCollection, ProjectCollection


def test_package_import():
    """Verify op package imports cleanly.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    assert op is not None


def test_date_string_format():
    """Verify date_string returns a formatted date string matching "%A, %d %B %Y".

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    formatted = date_string()
    # Parsing with strptime validates expected format
    parsed = datetime.datetime.strptime(formatted, "%A, %d %B %Y")
    assert parsed.year == datetime.datetime.now().year


def test_get_dashboard_data_empty(isolated_storage_dir: Path):
    """Verify get_dashboard_data aggregates empty counts correctly.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    data = get_dashboard_data()
    assert data["num_buckets"] == 0
    assert data["active_projects"] == 0
    assert data["active_tickets"] == 0
    assert data["active_habits"] == 0


def test_get_dashboard_data_populated(isolated_storage_dir: Path, sample_base_data: dict):
    """Verify get_dashboard_data aggregates populated model data accurately.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    sample_base_data["bucket"] = {"b1": {"text": "item1"}, "b2": {"text": "item2"}}
    sample_base_data["projects"] = {"p1": {"state": "active"}}
    sample_base_data["tickets"] = {"t1": {"state": "active"}, "t2": {"state": "done"}}
    sample_base_data["habits"] = {"h1": {"state": "active"}}
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    data = get_dashboard_data()
    assert data["num_buckets"] == 2
    assert data["active_projects"] == 1
    assert data["active_tickets"] == 1
    assert data["active_habits"] == 1


def test_add_new_bucket_item(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify add_new_bucket_item persists item and displays confirmation output.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    add_new_bucket_item("Write unit tests")
    captured = capsys.readouterr()
    assert "New bucket item captured:" in captured.out
    assert "Write unit tests" in captured.out

    bucket_col = BucketCollection()
    assert bucket_col.count_all_buckets() == 1


def test_list_bucket_items_empty(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify list_bucket_items handles an empty bucket cleanly.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    list_bucket_items()
    captured = capsys.readouterr()
    assert "BUCKET - 0 items" in captured.out
    assert "No items in bucket" in captured.out


def test_list_bucket_items_populated(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify list_bucket_items formats and lists bucket entries.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    bucket_col = BucketCollection()
    bucket_col.create("Read chapter 5")
    bucket_col.create("Call dentist")

    list_bucket_items()
    captured = capsys.readouterr()
    assert "BUCKET - 2 items" in captured.out
    assert "Read chapter 5" in captured.out
    assert "Call dentist" in captured.out


def test_list_bucket_items_ordering(isolated_storage_dir: Path, sample_base_data: dict, capsys: pytest.CaptureFixture):
    """Verify list_bucket_items sorts newest items first.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    sample_base_data["bucket"] = {
        "b1": {"item": "Oldest item", "date_created": "2026-08-01"},
        "b2": {"item": "Newest item", "date_created": "2026-08-16"},
        "b3": {"item": "Middle item", "date_created": "2026-08-10"},
    }
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    list_bucket_items()
    captured = capsys.readouterr()
    
    pos_newest = captured.out.find("Newest item")
    pos_middle = captured.out.find("Middle item")
    pos_oldest = captured.out.find("Oldest item")

    assert pos_newest < pos_middle < pos_oldest


def test_show_bucket_item_found(isolated_storage_dir: Path, sample_base_data: dict, capsys: pytest.CaptureFixture):
    """Verify show_bucket_item_by_id renders item details when found.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    sample_base_data["bucket"]["770e8400-e29b-41d4-a716-446655440000"] = {
        "item": "Detailed capture description",
        "date_created": "2026-08-16",
        "status": "fresh",
    }
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    show_bucket_item_by_id("770e8400")
    captured = capsys.readouterr()
    assert "ID: 770e8400-e29b-41d4-a716-446655440000" in captured.out
    assert "Created: 2026-08-16" in captured.out
    assert "Detailed capture description" in captured.out


def test_show_bucket_item_not_found(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify show_bucket_item_by_id renders error message when item is missing.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    show_bucket_item_by_id("99999999")
    captured = capsys.readouterr()
    assert "No bucket found with an ID starting with 99999999" in captured.out


def test_discard_bucket_item_found(isolated_storage_dir: Path, sample_base_data: dict, capsys: pytest.CaptureFixture):
    """Verify discard_bucket_item_by_id deletes item and prints success message.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    sample_base_data["bucket"]["330e8400-e29b-41d4-a716-446655440000"] = {
        "item": "Discardable note",
        "date_created": "2026-08-16",
        "status": "fresh",
    }
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    discard_bucket_item_by_id("330e8400")
    captured = capsys.readouterr()
    assert "Bucket item has been discarded successfully" in captured.out

    bucket_col = BucketCollection()
    assert bucket_col.count_all_buckets() == 0


def test_discard_bucket_item_not_found(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify discard_bucket_item_by_id prints not found message when item doesn't exist.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    discard_bucket_item_by_id("00000000")
    captured = capsys.readouterr()
    assert "No bucket item with ID found, no action taken" in captured.out


def test_create_project_by_id_bucket_not_found(isolated_storage_dir: Path, capsys: pytest.CaptureFixture):
    """Verify create_project_by_id exits with error when bucket item does not exist.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    create_project_by_id("missing-id")
    captured = capsys.readouterr()
    assert "Project creation failed, no bucket with ID: missing-id" in captured.out


def test_create_project_by_id_success(isolated_storage_dir: Path, sample_base_data: dict, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
    """Verify create_project_by_id interactively creates active project and deletes original bucket item.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    bucket_id = "440e8400-e29b-41d4-a716-446655440000"
    sample_base_data["bucket"][bucket_id] = {
        "item": "Convert to full project",
        "date_created": "2026-08-16",
        "status": "fresh",
    }
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    # Mock interactive terminal inputs: name, spec, done_when, active y/n
    user_inputs = iter(["Treehouse Build", "Build in the backyard oak", "Finished roof and paint", "yes"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(user_inputs))

    create_project_by_id("440e8400")
    captured = capsys.readouterr()

    assert "Created project" in captured.out
    assert "Active" in captured.out
    assert "Name: Treehouse Build" in captured.out
    assert "Project Spec: Build in the backyard oak" in captured.out
    assert "Done When: Finished roof and paint" in captured.out

    # Verify bucket item was removed
    bucket_col = BucketCollection()
    assert bucket_col.count_all_buckets() == 0

    # Verify project was created in storage
    project_col = ProjectCollection()
    projects = project_col.read_all("projects")
    assert len(projects) == 1
    created_proj = list(projects.values())[0]
    assert created_proj["name"] == "Treehouse Build"
    assert created_proj["spec"] == "Build in the backyard oak"
    assert created_proj["state"] == "active"
    assert created_proj["done_when"] == "Finished roof and paint"
    assert project_col.count_active_projects() == 1


def test_create_project_by_id_inactive(isolated_storage_dir: Path, sample_base_data: dict, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture):
    """Verify create_project_by_id interactively creates inactive project when user answers 'n'.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    bucket_id = "550e8400-e29b-41d4-a716-446655440000"
    sample_base_data["bucket"][bucket_id] = {
        "item": "Someday project idea",
        "date_created": "2026-08-16",
        "status": "fresh",
    }
    with open(isolated_storage_dir / "planner.json", "w") as f:
        json.dump(sample_base_data, f)

    user_inputs = iter(["Learn French", "Grammar and vocabulary", "B2 level", "n"])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(user_inputs))

    create_project_by_id("550e8400")
    captured = capsys.readouterr()

    assert "Created project" in captured.out
    assert "Not_Started" in captured.out

    project_col = ProjectCollection()
    projects = project_col.read_all("projects")
    assert len(projects) == 1
    created_proj = list(projects.values())[0]
    assert created_proj["state"] == "not_started"
    assert project_col.count_active_projects() == 0
