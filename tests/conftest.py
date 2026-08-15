"""Shared test fixtures for OP testing suite.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import json
import os
from pathlib import Path
import sys
import pytest

# Ensure the src/ directory is discoverable by pytest in src-layout setups
# Authored by Antigravity Agent (Gemini 3.7 Flash)
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from op.config import BASE_STRUCTURE
import op.storage as storage_module


@pytest.fixture
def sample_base_data() -> dict:
    """Fixture providing a copy of the canonical BASE_STRUCTURE.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    return {k: dict(v) for k, v in BASE_STRUCTURE.items()}


@pytest.fixture
def isolated_storage_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Fixture that configures an isolated temporary directory for OP_DATA_DIR.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    monkeypatch.setenv("OP_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(storage_module, "DATA_DIR", tmp_path)
    return tmp_path
