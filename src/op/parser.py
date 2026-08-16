"""Create parser for command line arguments"""

import argparse


def build_parser():
    """Parse cmd line args

    DEV NOTES (DELETE LATER):
        bucket      subcommand
        add         subcommand
        "text"      positional argument
        --date      optional argument
        --review    optional argument

    :return: parser
    :rtype: argparser.ArgumentParser
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    bucket_parser = subparsers.add_parser('bucket')
    bucket_subparsers = bucket_parser.add_subparsers(
        dest="bucket_command"
    )
    add_parser = bucket_subparsers.add_parser("add")
    add_parser.add_argument("text", type=str)
    return parser
