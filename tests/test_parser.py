"""Unit tests for CLI argument parsing in op.parser.

# Authored by Antigravity Agent (Gemini 3.7 Flash)
# License: MIT
"""

import pytest
from op.parser import build_parser


class TestParser:
    """Tests for CLI argument parser.

    # Authored by Antigravity Agent (Gemini 3.7 Flash)
    """

    def test_parser_no_args(self):
        """Verify parsing with no arguments defaults to command=None.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args([])
        assert args.command is None

    def test_parser_bucket_add(self):
        """Verify parsing 'bucket add <text>' captures subcommands and text.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["bucket", "add", "Buy groceries"])
        assert args.command == "bucket"
        assert args.bucket_command == "add"
        assert args.text == "Buy groceries"

    def test_parser_bucket_list(self):
        """Verify parsing 'bucket list' captures bucket and list subcommands.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["bucket", "list"])
        assert args.command == "bucket"
        assert args.bucket_command == "list"

    def test_parser_bucket_show(self):
        """Verify parsing 'bucket show <id>' captures bucket, show, and id argument.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["bucket", "show", "a1b2c3d4"])
        assert args.command == "bucket"
        assert args.bucket_command == "show"
        assert args.id == "a1b2c3d4"

    def test_parser_bucket_discard(self):
        """Verify parsing 'bucket discard <id>' captures bucket, discard, and id argument.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["bucket", "discard", "a1b2c3d4"])
        assert args.command == "bucket"
        assert args.bucket_command == "discard"
        assert args.id == "a1b2c3d4"
