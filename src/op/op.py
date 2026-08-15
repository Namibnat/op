"""Operational planner that runs a text base GTD planner, routine manager and personal logger"""

import datetime
import os
import shutil

from op.models import BucketCollection, ProjectCollection


def date_string():
    """Create a formatted date string for printing

    :return: Formatted date string
    :rtype: str
    """
    date = datetime.datetime.now()
    return date.strftime("%A, %d %B %Y")


def print_dashboard(dashboard_data: dict):
    """Print the dashboard

    :param dashboard_data: Dashboard data
    """
    formatted_date = date_string()
    terminal_width = shutil.get_terminal_size().columns
    full_line = "_" * terminal_width
    item_sep = f"\n\n\n{full_line}\n\n"

    title_line = f" OP - {formatted_date} "
    len_title_line = len(title_line)
    short_line = int((terminal_width / 2) - (len_title_line / 2))
    title_line_full = "-" * short_line + title_line + "-" * short_line

    # Dashboard Data
    num_of_buckets = dashboard_data.get('num_buckets')
    num_of_active_projects = dashboard_data.get('active_projects')
    num_of_active_tickets = 0
    num_of_active_routines = 0

    os.system('clear')
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

    return dashboard_data


def main():
    dashboard_data = get_dashboard_data()
    print_dashboard(dashboard_data)
