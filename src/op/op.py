"""Operational planner that runs a text base GTD planner, routine manager and personal logger"""

import datetime
import os
import shutil

from op.models import BucketCollection, ProjectCollection, TicketCollection, RoutinesCollection
from op.parser import build_parser
from op.schema import ProjectState, Project, ProjectResource


def date_string() -> str:
    """Create a formatted date string for printing

    :return: Formatted date string
    """
    date = datetime.datetime.now()
    return date.strftime("%A, %d %B %Y")


def create_item_seperator(terminal_width: int) -> str:
    """Create item separator

    :param terminal_width: The width of the terminal window as an int
    :return: Formatting to add space between items
    """
    full_line = "_" * terminal_width
    item_sep = f"\n\n\n{full_line}\n\n"
    return item_sep


def create_title_line(terminal_width: int) -> str:
    """Create the top title line

    :param terminal_width: The width of the terminal window as an int
    :return: Title Line
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


def add_new_bucket_item(text: str):
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


def list_bucket_items():
    """List all the items in the bucket"""
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    bucket_interface = BucketCollection()
    all_buckets = bucket_interface.get_all_buckets()
    if all_buckets:
        # Show newest items first
        all_buckets.sort(key=lambda x: x.date_created, reverse=True)

    # The first part is 22 characters, and add some space at the end of the line
    reasonable_item_length = max(10, terminal_width - 40)

    bucket_items_string = "\tNo items in bucket"
    num_buckets = 0

    if all_buckets:
        print_lines = list()
        for bucket in all_buckets:
            created_date = bucket.date_created
            item = bucket.item
            primary_key = bucket.pk[:8]
            print_line = f"{primary_key}  {created_date}  {item[:reasonable_item_length]}"
            print_lines.append(print_line)

        bucket_items_string = "\n\t".join(print_lines)
        num_buckets = len(all_buckets)

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" BUCKET - {num_buckets} items"
        f"{item_sep}"
        f"\t{bucket_items_string}"
        f"{item_sep}"
    )
    print(display)


def show_bucket_item_by_id(pk: str):
    """Show a bucket item based on a given ID

    :param pk: A bucket ID
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    bucket_interface = BucketCollection()
    bucket = bucket_interface.get_bucket(pk.strip())

    bucket_output = f"\nNo bucket found with an ID starting with {pk.strip()}"
    if bucket:
        bucket_id = bucket.pk
        created_date = bucket.date_created
        item = bucket.item
        bucket_output = f"ID: {bucket_id[:8]}\n[Created: {created_date}]\n\n{item}"

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" BUCKET"
        f"{item_sep}"
        f"{bucket_output}"
        f"{item_sep}"
    )
    print(display)


def discard_bucket_item_by_id(pk: str):
    """Discard a bucket item

    :param pk: A bucket ID
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    status_message = "No bucket item with ID found, no action taken"

    bucket_interface = BucketCollection()
    discard_status = bucket_interface.discard_bucket(pk.strip())
    if discard_status:
        status_message = "Bucket item has been discarded successfully"

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" BUCKET"
        f"{item_sep}"
        f"\t{status_message}"
        f"{item_sep}"
    )
    print(display)


def create_project_by_id(pk: str):
    """Create a project by a bucket ID

    Take a bucket item and turn it into a project.  Discard the bucket on success.

    Once again, there is a bit of philosophy here.  Buckets (ideas) are cheap, and projects
    will be editable, so there isn't going to be a long "are you happy" loop.  Make the project
    and delete the bucket all in one go.

    :param pk: A bucket ID
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)

    bucket_interface = BucketCollection()
    if not bucket_interface.get_bucket(pk.strip()):
        title_line_full = create_title_line(terminal_width)

        display = (
            "\n\n"
            f"{title_line_full}"
            "\n\n\n"
            f"\tProject creation failed, no bucket with ID: {pk.strip()}\n"
        )
        print(display)
        return

    show_bucket_item_by_id(pk)

    display = (
        f"\tCreate project...\n"
    )
    print(display)

    project_state = 'not_started'
    project_name = input("Name the project: ")
    project_spec = input("Describe the project in more detail: ")
    project_done_when = input("Describe the conditions to be met to call this project done: ")
    raw_state = input("Type Y if the project is active now: y/n ")
    if raw_state.lower().strip().startswith('y'):
        project_state = 'active'

    new_project_item = Project.model_validate(
        {
            'name': project_name,
            'spec': project_spec,
            'state': project_state,
            'done_when': project_done_when,
            'date_created': datetime.date.today()
        }
    )

    project_interface = ProjectCollection()
    new_project = project_interface.create(new_project_item)

    os.system('clear')
    show_bucket_item_by_id(pk)

    bucket_interface = BucketCollection()
    bucket_interface.discard_bucket(pk.strip())

    project_state = new_project.state
    primary_key = new_project.pk[:8]

    display = (
        " PROJECT"
        "\n"
        f"Created project [{primary_key} - {project_state.title()}]\n"
        f"\tName: {new_project.name}\n"
        f"\tProject Spec: {new_project.spec}\n"
        f"\tDone When: {new_project.done_when}\n"
        f"\tCreated: {new_project.date_created}\n"
        f"{item_sep}"
        f"Bucket {pk} deleted."
    )

    print(display)


def list_project_items(args):
    """List all projects"""
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    project_interface = ProjectCollection()

    # Filter: by default filter by active
    project_filter = 'active'
    if args.all:
        project_filter = 'all'
    elif args.state:
        project_filter = args.state

    all_projects = project_interface.get_filtered_projects(project_filter)
    if all_projects:
        # Show newest items first
        all_projects.sort(key=lambda x: x.date_created, reverse=True)

    # The first part is 22 characters, and add some space at the end of the line
    reasonable_item_length = max(10, terminal_width - 40)

    bucket_items_string = "\tNo projects"
    len_all_projects = 0

    if all_projects:
        print_lines = list()
        for project in all_projects:
            created_date = project.date_created
            name = project.name
            primary_key = project.pk[:8]
            print_line = f"{primary_key}  {created_date}  {name[:reasonable_item_length]}"
            print_lines.append(print_line)

        bucket_items_string = "\n\t".join(print_lines)
        len_all_projects = len(all_projects)

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" PROJECTS - {len_all_projects} projects"
        f"{item_sep}"
        f"\t{bucket_items_string}"
        f"{item_sep}"
    )
    print(display)


def show_project_by_id(pk: str, state_update: bool = False):
    """Show a single project by ID

    :param pk: Project ID
    :param state_update: Was the state updated
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    project_interface = ProjectCollection()
    project = project_interface.get_project(pk.strip())

    project_output = f"\nNo project found with an ID starting with {pk.strip()}"
    if project:
        project_id = project.pk[:8]
        name = project.name
        spec = project.spec
        state = project.state.title()
        done_when = project.done_when
        date_created = project.date_created
        resources = project.resources

        resources_output = ''
        resource_output_collection = list()

        if resources:
            resources_output = '\nPROJECT RESOURCES:\n--------------------------------------\n'
            for resource_key, resource in resources.items():
                resource_output = (
                    f"Type:     {resource.type}\n"
                    f"Label:    {resource.label}\n"
                    f"Location: {resource.location}\n"
                )
                resource_output_collection.append(resource_output)
            resources_output = resources_output + '\n'.join(resource_output_collection)

        state_output = f"State: [{state}]"
        if state_update:
            state_output = f"\nUpdated State: [{state}]"

        project_output = (
            f"ID: {project_id}\n"
            f"[Created: {date_created}]\n\n"
            f"{name}\n\n"
            f"Project spec:\n\t{spec}\n\n"
            f"Done when:\n\t{done_when}\n\n"
            f"{state_output}\n"
            f"{resources_output}"
        )

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" PROJECT"
        f"{item_sep}"
        f"{project_output}"
        f"{item_sep}"
    )
    print(display)


def set_project_by_id(pk: str):
    """Set a project state

    State can be set to:
        not_started
        active
        done
        archived

    :param pk: Project ID
    """
    project_interface = ProjectCollection()

    # Display it
    show_project_by_id(pk)

    if not project_interface.get_project(pk.strip()):
        return

    print("Choose state (enter the number)\n\n")

    for index, possible_state in enumerate(ProjectState, start=1):
        print(f" - {index}: {possible_state.value}")

    print()

    choice = input("% ")
    choice = choice.strip()
    if not choice.isdigit() or int(choice) not in range(1, len(ProjectState) + 1):
        print(f"Invalid choice {choice}, try again")
        return

    choice_value = int(choice)

    state = list(ProjectState)[choice_value - 1]
    project_interface.set_project_state(pk, state)

    os.system('clear')
    # Display it after update
    show_project_by_id(pk, state_update=True)


def add_project_resources(pk):
    """Add project resources

    :param pk: Project ID
    """
    project_interface = ProjectCollection()

    # Display it
    show_project_by_id(pk)

    project = project_interface.get_project(pk.strip())
    if not project:
        return

    new_resources = 0
    while True:
        print("Add a new resource or hit enter to save them")
        resource_type = input("Resource Type: ")
        if not resource_type.strip():
            break
        resource_label = input("Resource Label: ")
        resource_location = input("Resource Location: ")

        new_resource = ProjectResource.model_validate(
            {
                "type": resource_type,
                "label": resource_label,
                "location": resource_location
            }
        )
        project_interface.add_project_resource(
            project.pk,
            new_resource
        )
        new_resources += 1

    if not new_resources:
        print("No resources added")
        return

    os.system('clear')
    show_project_by_id(project.pk)


def handle_project_resources(args):
    if args.add:
        add_project_resources(args.add)


def main():
    """Run op"""
    parser = build_parser()
    args = parser.parse_args()

    os.system('clear')

    # Bucket related actions
    if args.command == "bucket":
        if args.bucket_command == "add":
            add_new_bucket_item(args.text)
        elif args.bucket_command == "list":
            list_bucket_items()
        elif args.bucket_command == "show":
            show_bucket_item_by_id(args.id)
        elif args.bucket_command == "discard":
            discard_bucket_item_by_id(args.id)
        else:
            list_bucket_items()

    # Project related actions
    elif args.command == "project":
        if args.project_command == "create":
            create_project_by_id(args.id)
        elif args.project_command == "list":
            list_project_items(args)
        elif args.project_command == "show":
            show_project_by_id(args.id)
        elif args.project_command == "set":
            set_project_by_id(args.id)
        elif args.project_command == "resources":
            handle_project_resources(args)
        else:
            list_project_items(args)

    # Dashboard
    else:
        dashboard_data = get_dashboard_data()
        print_dashboard(dashboard_data)
