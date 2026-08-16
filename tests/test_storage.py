"""Unit and integration tests for storage operations in op.storage.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import json
from pathlib import Path
import pytest

from op.config import BASE_STRUCTURE
from op.storage import JsonContainer


class TestJsonContainerValidation:
    """Tests for JsonContainer structure validation logic.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_initial_state_has_base_structure(self):
        """Verify JsonContainer initializes with default BASE_STRUCTURE data and planner path.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        assert container.data == BASE_STRUCTURE
        assert container.filename == "planner.json"
        assert container.planner.name == "planner.json"

    def test_validate_structure_success(self, sample_base_data: dict):
        """Verify _validate_structure passes on a valid complete dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        container.data = sample_base_data
        # Should execute without raising any exception
        container._validate_structure()

    def test_validate_structure_fails_when_not_a_dict(self):
        """Verify _validate_structure raises ValueError when data is not a dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        container.data = ["invalid", "list", "structure"]
        with pytest.raises(ValueError, match="The structure of the planner.json file is not valid"):
            container._validate_structure()

    @pytest.mark.parametrize("missing_key", list(BASE_STRUCTURE.keys()))
    def test_validate_structure_fails_when_missing_key(self, sample_base_data: dict, missing_key: str):
        """Verify _validate_structure raises ValueError when any base key is missing.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        del sample_base_data[missing_key]
        container.data = sample_base_data
        with pytest.raises(ValueError, match=f"Container missing top level key: {missing_key}"):
            container._validate_structure()


class TestJsonContainerFileOperations:
    """Tests for JsonContainer disk reads, writes, and auto-creation.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_create_container_writes_file(self, isolated_storage_dir: Path):
        """Verify _create_container writes the BASE_STRUCTURE JSON to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        container._create_container()

        target_file = isolated_storage_dir / "planner.json"
        assert target_file.exists()

        with open(target_file, "r") as f:
            disk_data = json.load(f)
        assert disk_data == BASE_STRUCTURE

    def test_read_container_loads_and_validates_data(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify _read_container successfully reads and parses file contents.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["bucket"]["item-1"] = {"text": "Test capture item"}
        target_file = isolated_storage_dir / "planner.json"
        with open(target_file, "w") as f:
            json.dump(sample_base_data, f)

        container = JsonContainer()
        loaded = container._read_container()

        assert loaded == sample_base_data
        assert container.data == sample_base_data
        assert "item-1" in container.data["bucket"]

    def test_read_auto_creates_if_missing(self, isolated_storage_dir: Path):
        """Verify read() automatically initializes the file if it does not exist.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        target_file = isolated_storage_dir / "planner.json"
        assert not target_file.exists()

        container = JsonContainer()
        data = container.read()

        assert target_file.exists()
        assert data == BASE_STRUCTURE
        assert container.data == BASE_STRUCTURE

    def test_read_reads_existing_file(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify read() loads existing data without overwriting it.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        sample_base_data["projects"]["proj-1"] = {"name": "Test Project"}
        target_file = isolated_storage_dir / "planner.json"
        with open(target_file, "w") as f:
            json.dump(sample_base_data, f)

        container = JsonContainer()
        data = container.read()

        assert data["projects"]["proj-1"]["name"] == "Test Project"
        assert container.data["projects"]["proj-1"]["name"] == "Test Project"

    def test_create_item_persists_to_disk(self, isolated_storage_dir: Path):
        """Verify create() adds a new UUID-keyed entry to the container and saves to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        new_item = {"item": "Test capture", "date_created": "2026-08-16"}
        container.create(new_item, container_name="bucket")

        target_file = isolated_storage_dir / "planner.json"
        assert target_file.exists()
        with open(target_file, "r") as f:
            saved_data = json.load(f)

        assert len(saved_data["bucket"]) == 1
        created_id = list(saved_data["bucket"].keys())[0]
        assert saved_data["bucket"][created_id] == new_item

    def test_create_item_invalid_container_raises_value_error(self, isolated_storage_dir: Path):
        """Verify create() raises ValueError when given an invalid container name.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        with pytest.raises(ValueError, match="No container named nonexistent exists"):
            container.create({"text": "abc"}, container_name="nonexistent")

    def test_create_item_invalid_type_raises_value_error(self, isolated_storage_dir: Path):
        """Verify create() raises ValueError when new_item is not a dictionary.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        with pytest.raises(ValueError, match="New Item not of type <dict>"):
            container.create("not-a-dict", container_name="bucket")

    def test_save_persists_current_data(self, isolated_storage_dir: Path, sample_base_data: dict):
        """Verify save() writes modified container data to disk.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        container = JsonContainer()
        sample_base_data["bucket"]["custom-id"] = {"item": "Saved manually"}
        container.data = sample_base_data
        container.save()

        target_file = isolated_storage_dir / "planner.json"
        assert target_file.exists()
        with open(target_file, "r") as f:
            disk_data = json.load(f)

        assert "custom-id" in disk_data["bucket"]
        assert disk_data["bucket"]["custom-id"]["item"] == "Saved manually"
