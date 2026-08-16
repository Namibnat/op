"""High-level integration and CLI entrypoint smoke tests.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import datetime
import json
from pathlib import Path
import pytest

import op
from op.op import date_string, get_dashboard_data


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
