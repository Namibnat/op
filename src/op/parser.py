"""Create parser for command line arguments"""

import argparse


def build_parser():
    """Parse cmd line args

    :return: parser
    :rtype: argparser.ArgumentParser
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

    return parser
