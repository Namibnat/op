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

    def test_parser_project_create(self):
        """Verify parsing 'project create <id>' captures project, create, and id argument.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "create", "a1b2c3d4"])
        assert args.command == "project"
        assert args.project_command == "create"
        assert args.id == "a1b2c3d4"

    def test_parser_project_list(self):
        """Verify parsing 'project list' captures project and list subcommands.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "list"])
        assert args.command == "project"
        assert args.project_command == "list"
        assert args.all is False
        assert args.state is None

    def test_parser_project_list_all(self):
        """Verify parsing 'project list --all' sets all flag to True.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "list", "--all"])
        assert args.command == "project"
        assert args.project_command == "list"
        assert args.all is True

    @pytest.mark.parametrize("state_val", ["new", "done", "archived"])
    def test_parser_project_list_state(self, state_val: str):
        """Verify parsing 'project list --state <choice>' captures the state filter.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "list", "--state", state_val])
        assert args.command == "project"
        assert args.project_command == "list"
        assert args.state == state_val

    def test_parser_project_show(self):
        """Verify parsing 'project show <id>' captures project, show, and id argument.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "show", "b2c3d4e5"])
        assert args.command == "project"
        assert args.project_command == "show"
        assert args.id == "b2c3d4e5"

    def test_parser_project_set(self):
        """Verify parsing 'project set <id>' captures project, set, and id argument.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "set", "c3d4e5f6"])
        assert args.command == "project"
        assert args.project_command == "set"
        assert args.id == "c3d4e5f6"

    def test_parser_project_resources_add(self):
        """Verify parsing 'project resources --add <id>' captures project, resources, and add id.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "resources", "--add", "d4e5f6a7"])
        assert args.command == "project"
        assert args.project_command == "resources"
        assert args.add == "d4e5f6a7"

    def test_parser_project_resources_remove(self):
        """Verify parsing 'project resources --remove <id>' captures project, resources, and remove id.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["project", "resources", "--remove", "e5f6a7b8"])
        assert args.command == "project"
        assert args.project_command == "resources"
        assert args.remove == "e5f6a7b8"

    def test_parser_ticket_create_no_id(self):
        """Verify parsing 'ticket create' defaults id to None.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "create"])
        assert args.command == "ticket"
        assert args.ticket_command == "create"
        assert args.id is None

    def test_parser_ticket_create_with_id(self):
        """Verify parsing 'ticket create <id>' captures optional id.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "create", "f7a8b9c0"])
        assert args.command == "ticket"
        assert args.ticket_command == "create"
        assert args.id == "f7a8b9c0"

    def test_parser_ticket_list(self):
        """Verify parsing 'ticket list' captures ticket and list subcommands with default flags.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "list"])
        assert args.command == "ticket"
        assert args.ticket_command == "list"
        assert args.all is False
        assert args.state is None

    def test_parser_ticket_list_all(self):
        """Verify parsing 'ticket list --all' sets all flag to True.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "list", "--all"])
        assert args.command == "ticket"
        assert args.ticket_command == "list"
        assert args.all is True

    @pytest.mark.parametrize("state_val", ["open", "in_progress", "done"])
    def test_parser_ticket_list_state(self, state_val: str):
        """Verify parsing 'ticket list --state <choice>' captures valid state choices.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "list", "--state", state_val])
        assert args.command == "ticket"
        assert args.ticket_command == "list"
        assert args.state == state_val

    def test_parser_ticket_list_invalid_state_raises(self):
        """Verify parsing 'ticket list --state <invalid>' exits with parse error.

        # Authored by Antigravity Agent (Gemini 3.7 Flash)
        """
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["ticket", "list", "--state", "invalid_state"])

    def test_parser_ticket_show(self):
        """Verify parsing 'ticket show <id>' captures ticket, show, and id argument.

        Prepared test-first for T-102 (spec §5).

        # Authored by Claude Code (claude-sonnet-5) for T-102 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "show", "a1b2c3d4"])
        assert args.command == "ticket"
        assert args.ticket_command == "show"
        assert args.id == "a1b2c3d4"

    def test_parser_ticket_show_missing_id_raises(self):
        """Verify parsing 'ticket show' with no positional id exits with a parse error.

        # Authored by Claude Code (claude-sonnet-5) for T-102 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["ticket", "show"])

    def test_parser_ticket_set(self):
        """Verify parsing 'ticket set <id>' captures ticket, set, and id argument.

        Prepared test-first for T-103 (spec §5).

        # Authored by Claude Code (claude-sonnet-5) for T-103 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "set", "b2c3d4e5"])
        assert args.command == "ticket"
        assert args.ticket_command == "set"
        assert args.id == "b2c3d4e5"

    def test_parser_ticket_set_missing_id_raises(self):
        """Verify parsing 'ticket set' with no positional id exits with a parse error.

        # Authored by Claude Code (claude-sonnet-5) for T-103 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["ticket", "set"])

    def test_parser_ticket_edit(self):
        """Verify parsing 'ticket edit <id>' captures ticket, edit, and id argument.

        Prepared test-first for T-105 (spec §5).

        # Authored by Claude Code (claude-sonnet-5) for T-105 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        args = parser.parse_args(["ticket", "edit", "c3d4e5f6"])
        assert args.command == "ticket"
        assert args.ticket_command == "edit"
        assert args.id == "c3d4e5f6"

    def test_parser_ticket_edit_missing_id_raises(self):
        """Verify parsing 'ticket edit' with no positional id exits with a parse error.

        # Authored by Claude Code (claude-sonnet-5) for T-105 test-first coverage.
        # License: MIT
        """
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["ticket", "edit"])


