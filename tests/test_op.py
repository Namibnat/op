"""High-level integration and CLI entrypoint smoke tests.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import pytest
import op


def test_package_import():
    """Verify op package imports cleanly.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """
    assert op is not None
