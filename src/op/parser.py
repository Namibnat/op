"""Create parser for command line arguments"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Parse cmd line args

    :return: parser
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    # ---- Bucket Args ----------------------------
    bucket_parser = subparsers.add_parser('bucket')
    bucket_subparsers = bucket_parser.add_subparsers(
        dest="bucket_command"
    )

    add_bucket_parser = bucket_subparsers.add_parser("add")
    add_bucket_parser.add_argument("text", type=str)

    show_bucket_parser = bucket_subparsers.add_parser("show")
    show_bucket_parser.add_argument("id", type=str)

    discard_bucket_parser = bucket_subparsers.add_parser("discard")
    discard_bucket_parser.add_argument("id", type=str)

    bucket_subparsers.add_parser("list")

    # ---- Project Args ----------------------------
    project_parser = subparsers.add_parser('project')
    project_subparsers = project_parser.add_subparsers(
        dest="project_command"
    )

    create_project_parser = project_subparsers.add_parser("create")
    create_project_parser.add_argument("id", type=str)

    show_project_parser = project_subparsers.add_parser("show")
    show_project_parser.add_argument("id", type=str)

    list_project_parser = project_subparsers.add_parser("list")
    list_project_parser.add_argument(
        "--state",
        choices=["new", "done", "archived"],
    )
    list_project_parser.add_argument(
        "--all",
        action="store_true",
    )

    set_project_parser = project_subparsers.add_parser("set")
    set_project_parser.add_argument("id", type=str)

    resource_project_parser = project_subparsers.add_parser("resources")
    resource_project_parser.add_argument("--add", type=str)
    resource_project_parser.add_argument("--remove", type=str)

    # ---- Ticket Args ----------------------------

    ticket_parser = subparsers.add_parser('ticket')
    ticket_subparsers = ticket_parser.add_subparsers(
        dest="ticket_command"
    )
    create_ticket_parser = ticket_subparsers.add_parser("create")
    create_ticket_parser.add_argument("id", nargs="?", type=str)

    list_ticket_parser = ticket_subparsers.add_parser("list")
    list_ticket_parser.add_argument(
        "--state",
        choices=["open", "in_progress", "done"],
    )
    list_ticket_parser.add_argument(
        "--all",
        action="store_true",
    )
    list_ticket_parser.add_argument(
        "-a", "--actionable",
        action="store_true",
    )

    show_ticket_parser = ticket_subparsers.add_parser("show")
    show_ticket_parser.add_argument("id", type=str)

    return parser
