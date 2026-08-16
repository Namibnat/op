"""Operational planner that runs a text base GTD planner, routine manager and personal logger"""

import datetime
import os
import shutil

from op.models import BucketCollection, ProjectCollection, TicketCollection, RoutinesCollection
from op.parser import build_parser


def date_string():
    """Create a formatted date string for printing

    :return: Formatted date string
    :rtype: str
    """
    date = datetime.datetime.now()
    return date.strftime("%A, %d %B %Y")


def create_item_seperator(terminal_width):
    """Create item separator

    :param terminal_width: The width of the terminal window as an int
    :return: Formatting to add space between items
    :rtype: str
    """
    full_line = "_" * terminal_width
    item_sep = f"\n\n\n{full_line}\n\n"
    return item_sep


def create_title_line(terminal_width):
    """Create the top title line

    :param terminal_width: The width of the terminal window as an int
    :return: Title Line
    :rtype: str
    """
    formatted_date = date_string()

    title_line = f" OP - {formatted_date} "
    len_title_line = len(title_line)
    short_line = int((terminal_width / 2) - (len_title_line / 2))
    title_line_full = "-" * short_line + title_line + "-" * short_line
    return title_line_full


def print_dashboard(dashboard_data: dict):
    """Print the dashboard

    :param dashboard_data: Dashboard data
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    # Dashboard Data
    num_of_buckets = dashboard_data.get('num_buckets')
    num_of_active_projects = dashboard_data.get('active_projects')
    num_of_active_tickets = dashboard_data.get('active_tickets')
    num_of_active_routines = dashboard_data.get('active_habits')

    dashboard = (
        "\n\n"
        f"{title_line_full}"
        "\n\n"
        " BUCKET"
        "\n"
        f"\t{num_of_buckets} unprocessed items"
        f"{item_sep}"
        " PROJECTS"
        "\n"
        f"\t{num_of_active_projects} active projects"
        f"{item_sep}"
        " TICKETS"
        "\n"
        f"\t{num_of_active_tickets} active tickets"
        f"{item_sep}"
        " TODAY"
        "\n"
        f"\t{num_of_active_routines} active routines"
        f"{item_sep}"
    )
    print(dashboard)


def get_dashboard_data():
    """Get the view of the data needed to fill the dashboard

    :return: Dashboard Data
    """
    dashboard_data = dict()

    bucket_interface = BucketCollection()
    dashboard_data['num_buckets'] = bucket_interface.count_all_buckets()

    project_interface = ProjectCollection()
    dashboard_data['active_projects'] = project_interface.count_active_projects()

    ticket_interface = TicketCollection()
    dashboard_data['active_tickets'] = ticket_interface.count_active_tickets()

    routines_interface = RoutinesCollection()
    dashboard_data['active_habits'] = routines_interface.count_active_habits()

    return dashboard_data


def add_new_bucket_item(text):
    """Add a new item to bucket

    :param text: Text to insert into a new bucket
    """
    new_bucket_item = text.strip()

    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    bucket_interface = BucketCollection()
    bucket_interface.create(new_bucket_item)

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n"
        " BUCKET"
        "\n"
        " New bucket item captured:"
        f"\n\t{text}"
        f"{item_sep}"
    )
    print(display)


def main():
    parser = build_parser()
    args = parser.parse_args()

    os.system('clear')

    if args.command == "bucket":
        if args.bucket_command == "add":
            add_new_bucket_item(args.text)
        else:
            parser.print_help()
    else:
        dashboard_data = get_dashboard_data()
        print_dashboard(dashboard_data)
