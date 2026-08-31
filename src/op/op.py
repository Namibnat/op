"""Operational planner that runs a text base GTD planner, routine manager and personal logger"""

import argparse
import datetime
import re
import shutil
from typing import Any, Callable

from op.models import BucketCollection, ProjectCollection, TicketCollection, RoutinesCollection
from op.parser import build_parser
from op.schema import ProjectState, Project, ProjectResource, TicketState, Ticket
from op.config import ID_DISPLAY_LENGTH


def console_clear():
    """Clear console"""
    print("\033[2J\033[H", end="")


def choice_input() -> str:
    """Get a choice from the user"""
    choice = input("% ")
    return choice.strip()


def date_string() -> str:
    """Create a formatted date string for printing

    :return: Formatted date string
    """
    date = datetime.datetime.now()
    return date.strftime("%A, %d %B %Y")


def output_id_string(pk: str) -> str:
    """Create a formatted id string for printing"""
    if not pk:
        raise ValueError("ID string cannot be empty")
    return pk[:ID_DISPLAY_LENGTH]


def create_item_seperator(terminal_width: int) -> str:
    """Create an item separator

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


def create_type_item_str(
        items: list[Any],
        item_length: int,
        get_label: Callable[[Any], str] = lambda x: getattr(x, "item", getattr(x, "name", "")),
        include_state: bool = False,
) -> str:
    """Create the type item string for printing

    :param items: The type of item
    :param item_length: The length of the item
    :param get_label: Function to get label
    :param include_state: Whether to include state information
    :return: Type item string
    """
    print_lines = list()
    state = ''
    for item in items:
        created_date = item.date_created
        name = get_label(item)
        primary_key = output_id_string(item.pk)
        if include_state and hasattr(item, 'state') and item.state:
            state = f"{item.state}  "
        print_line = f"{primary_key}  {created_date}  {state}{name[:item_length]}"
        print_lines.append(print_line)

    type_items_string = "\n\t".join(print_lines)
    return type_items_string


def parse_due_input(raw_date_input: str, allow_clear: bool = False) -> tuple[str | None, bool]:
    """Parse the due_date and time_bound.

    :param raw_date_input: User input, which could be a date or a dash to indicate clear
    :param allow_clear: Whether to allow clear date or not
    :return: Due date string and if the ticket is time-bound.
    """
    if not raw_date_input:
        return None, False

    if allow_clear and raw_date_input == "-":
        return None, True

    pattern_short_date = re.compile(r'^\d{4}-\d{2}-\d{2}')
    pattern_full_date = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$')

    if not re.search(r'\d{4}-\d{2}-\d{2}', raw_date_input):
        return None, False

    if re.search(pattern_short_date, raw_date_input):
        if not re.search(pattern_full_date, raw_date_input):
            return f"{raw_date_input} 00:00", True

        return raw_date_input, True

    return None, False


def print_dashboard(dashboard_data: dict):
    """Print the dashboard

    :param dashboard_data: Dashboard data
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    # Dashboard Data
    num_of_buckets = dashboard_data.get('num_buckets') or '0'
    num_of_active_projects = dashboard_data.get('active_projects') or '0'
    num_of_active_tickets = dashboard_data.get('active_tickets') or '0'
    num_of_active_routines = dashboard_data.get('active_habits') or '0'

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


def get_dashboard_data() -> dict:
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
        bucket_items_string = create_type_item_str(
            items=all_buckets,
            item_length=reasonable_item_length
        )
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
        bucket_id = output_id_string(bucket.pk)
        created_date = bucket.date_created
        item = bucket.item
        bucket_output = f"ID: {bucket_id}\n[Created: {created_date}]\n\n{item}"

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

    console_clear()
    show_bucket_item_by_id(pk)

    bucket_interface = BucketCollection()
    bucket_interface.discard_bucket(pk.strip())

    project_state = new_project.state
    primary_key = output_id_string(new_project.pk)

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


def list_project_items(args: argparse.Namespace):
    """List all projects

    :param args: command line arguments
    """
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

    project_items_string = "\tNo projects"

    if all_projects:
        project_items_string = create_type_item_str(
            items=all_projects,
            item_length=reasonable_item_length
        )

    len_all_projects = len(all_projects) if all_projects else 0

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" PROJECTS - {len_all_projects} projects"
        f"{item_sep}"
        f"\t{project_items_string}"
        f"{item_sep}"
    )
    print(display)


def show_project_by_id(
        pk: str,
        state_update: bool = False,
        deleted: bool = False
) -> Project | None:
    """Show a single project by ID

    :param pk: Project ID
    :param state_update: Was the state updated
    :param deleted: If a resource was deleted
    """
    pk = pk.strip()
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    project_interface = ProjectCollection()
    ticket_interface = TicketCollection()
    project = project_interface.get_project(pk)

    tickets_output = ''
    if project:
        project_tickets = ticket_interface.get_project_tickets(pk)
        ticket_output_collection = list()
        ticket_output_collection.append(
            '\n\nPROJECT TICKETS:\n--------------------------------------\n'
            'ID        Actionable  Title'
        )
        if project_tickets:
            for ticket in project_tickets:
                ticket_id = output_id_string(ticket.pk)
                actionable_str = "Y" if ticket.actionable else "N"

                ticket_output_collection.append(f"{ticket_id}  {actionable_str}  "
                                                f"         {ticket.title}\n")
            tickets_output = "\n".join(ticket_output_collection)

    project_output = f"\nNo project found with an ID starting with {pk.strip()}"
    if project:
        project_id = output_id_string(project.pk)
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
                resource_id = output_id_string(resource_key)
                resource_output = (
                    f"ID:       {resource_id}\n"
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
            f"{tickets_output}"
        )

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" PROJECT"
        f"{item_sep}"
        f"{project_output}"
    )
    print(display)

    if deleted:
        print("\nResource deleted...\n\n")
    print(f"{item_sep}")
    return project


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

    states = list(ProjectState.__members__.values())

    for index, possible_state in enumerate(states, start=1):
        print(f" - {index}: {possible_state.value}")

    print()

    choice = choice_input()
    if not choice.isdigit() or int(choice) not in range(1, len(ProjectState) + 1):
        print(f"Invalid choice {choice}, try again")
        return

    choice_value = int(choice)

    state: ProjectState = states[choice_value - 1]
    project_interface.set_project_state(pk, state)

    console_clear()
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

    console_clear()
    show_project_by_id(project.pk)


def remove_project_resources(pk: str):
    """Remove a project resource

    :param pk: Project ID
    """
    project_interface = ProjectCollection()
    project = show_project_by_id(pk)
    if not project:
        return

    print("Enter the resource ID to remove, or enter to cancel")
    partial_key = input("Key: ").strip()
    if not partial_key:
        print("Cancelled")
        return

    success = project_interface.delete_project_resource(project.pk, partial_key)
    if success:
        show_project_by_id(pk, deleted=success)
        return

    print("\nDelete failed\n")


def handle_project_resources(args):
    """Project Resource dispatch

    :param args: Resource parser args
    """
    if args.add:
        add_project_resources(args.add)
    if args.remove:
        remove_project_resources(args.remove)


def create_ticket(pk: str | None = None, is_project: bool = False) -> bool:
    """Create a ticket.

    If it gets a project ID, ticket becomes a project "action", otherwise
    it's a stand-alone ticket.

    :param pk: Project ID
    :param is_project: Is this a project
    :return: Success
    """
    ticket_interface = TicketCollection()

    print("Enter ticket details:\n")
    title = input("Title: ")
    print("Ticket state options:\n - 1. in progress\n - or hit enter")
    raw_state = input(": ").strip()
    state = TicketState.IN_PROGRESS if raw_state == '1' else TicketState.OPEN
    project = pk if is_project else None

    actionable = True  # Non-project tickets should always be able to be worked on
    if is_project:
        print("If this ticket can be worked on now\n - 1. Can be worked on now"
              "\n - or hit enter if still waiting on other tickets")
        raw_actionable = input(": ").strip()
        actionable = actionable if raw_actionable == '1' else False

    print("Type the context in which this can be worked on (e.g. 'home', 'shopping',"
          "and for adding multiple, make them comma separated")
    context = input(": ").strip()

    print("Input date if time bound (just hit enter if not). "
          "For date, use the following forms:\n"
          "'2026-10-12 11:30' for specific time\n"
          "'2026-10-12' for all day on specific date")

    time_bound = False
    due_at = None
    due_date_raw = input(": ").strip()
    if due_date_raw:
        due_at, time_bound = parse_due_input(due_date_raw)

    new_ticket_item = Ticket.model_validate(
        {
            'title': title,
            'state': state,
            "project": project,
            "actionable": actionable,
            "context": context,
            "date_created": datetime.date.today(),
            "date_completed": None,
            "time_bound": time_bound,
            "due_at": due_at
        }

    )

    ticket_interface.create(new_ticket_item)
    print("Ticket created")
    return True


def create_ticket_from_id(pk: str):
    """Create a ticket from an ID.

    Determine if the ID matches a bucket or project.

    :param pk: ID (project or bucket)
    """
    pk = pk.strip()
    project_interface = ProjectCollection()
    bucket_interface = BucketCollection()

    bucket = bucket_interface.get_bucket(pk)
    project = project_interface.get_project(pk)

    if bucket and project:
        print(f"ID matches multiple options, try a longer ID")
        return

    if bucket:
        show_bucket_item_by_id(bucket.pk)
        create_ticket()
        bucket_interface.discard_bucket(pk)
        return

    if project:
        show_project_by_id(project.pk)
        create_ticket(project.pk, is_project=True)
        return
    print(f"No bucket or project found matching ID {pk}")


def ticket_create_dispatch(args):
    """Ticket create dispatch

    :param args: To check for ID
    :return:
    """
    if args.id:
        create_ticket_from_id(args.id)
        return

    create_ticket()


def list_ticket_items(args: argparse.Namespace):
    """List ticket items

    :param args: CLI arguments
    """
    ticket_interface = TicketCollection()

    # Filter: by default filter by all
    ticket_filter = 'actionable'
    if args.all:
        ticket_filter = 'all'
    elif args.state:
        ticket_filter = args.state

    if ticket_filter == 'all':
        all_tickets = ticket_interface.get_all_tickets()
    elif ticket_filter == 'actionable':
        all_tickets = ticket_interface.get_actionable_tickets()
    else:
        all_tickets = ticket_interface.get_tickets_by_state(args.state)

    if not all_tickets:
        print("No tickets found")
        return

    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    len_all_tickets = len(all_tickets)
    all_tickets = sorted(all_tickets, key=lambda x: x.date_created, reverse=True)

    # The first part is 22 characters, and add some space at the end of the line
    reasonable_item_length = max(10, terminal_width - 40)

    ticket_items_string = "No tickets found"

    def get_title(item):
        return item.title

    if all_tickets:
        ticket_items_string = create_type_item_str(
            items=all_tickets,
            item_length=reasonable_item_length,
            get_label=get_title,
            include_state=True
        )

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" TICKETS - {len_all_tickets} tickets"
        f"{item_sep}"
        f"\t{ticket_items_string}"
        f"{item_sep}"
    )
    print(display)


def show_ticket_by_id(
        pk: str,
        state_update: bool = False,
        actionable_updated: bool = False,
        title_updated: bool = False,
        context_updated: bool = False,
        due_date_updated: bool = False,
):
    """Show ticket by id

    :param pk: Ticket ID
    :param state_update: True if the state was updated
    :param actionable_updated: True if the actionable was updated
    :param title_updated: True if the title was updated
    :param context_updated: True if the context was updated
    :param due_date_updated: True if the due date was updated
    """
    terminal_width = shutil.get_terminal_size().columns
    item_sep = create_item_seperator(terminal_width)
    title_line_full = create_title_line(terminal_width)

    ticket_interface = TicketCollection()
    project_interface = ProjectCollection()
    ticket = ticket_interface.get_ticket(pk.strip())

    ticket_output_line = f"\nNo ticket found with an ID starting with {pk.strip()}"

    if ticket:
        ticket_id = ticket.pk
        ticket_output_line = output_id_string(ticket_id)
        ticket_created = ticket.date_created
        ticket_title = ticket.title
        ticket_state = ticket.state
        ticket_actionable = ticket.actionable
        ticket_actionable_output = "Yes" if ticket_actionable else "No"

        ticket_project_output = "— (standalone)"
        ticket_project = ticket.project
        if ticket_project:
            project = project_interface.get_project(ticket_project)
            if project:
                project_id = output_id_string(project.pk)
                project_name = project.name
                ticket_project_output = f"{project_id}  {project_name}"
            else:
                ticket_project_output = f"{ticket_project} (project not found)"

        ticket_context = ticket.context
        ticket_context_output = ticket_context if ticket_context.strip() else " —"

        ticket_due = ticket.due_at if (ticket.time_bound and ticket.due_at) else " — (not time-bound)"
        ticket_completed = ticket.date_completed if ticket.date_completed else " —"

        ticket_id_line = f"ID: {ticket_output_line}"
        ticket_created_line = f"[Created: {ticket_created}]"
        ticket_title_line = f"\nTitle: {ticket_title}"
        if title_updated:
            ticket_title_line = f"Updated Title: {ticket_title}"
        ticket_state_line = f"State: [{ticket_state}]"
        if state_update:
            ticket_state_line = f"Updated State: [{ticket_state}]"
        ticket_actionable_line = f"Actionable: {ticket_actionable_output}"
        if actionable_updated:
            ticket_actionable_line = f"Updated Actionable: {ticket_actionable_output}"
        ticket_project_line = f"Project: {ticket_project_output}"
        ticket_context_line = f"Context: {ticket_context_output}"
        if context_updated:
            ticket_context_line = f"Updated Context: {ticket_context_output}"
        ticket_due_line = f"Due: {ticket_due}"
        if due_date_updated:
            ticket_due_line = f"Updated Due: {ticket_due}"
        ticket_complete_line = f"Completed: {ticket_completed}"

        ticket_output_line = "\n".join(
            [
                ticket_id_line,
                ticket_created_line,
                ticket_title_line,
                ticket_state_line,
                ticket_actionable_line,
                ticket_project_line,
                ticket_context_line,
                ticket_due_line,
                ticket_complete_line
            ]
        )

    display = (
        "\n\n"
        f"{title_line_full}"
        "\n\n\n"
        f" TICKET"
        f"{item_sep}"
        f"{ticket_output_line}"
        f"{item_sep}"
    )
    print(display)


def set_ticket_by_id(pk: str):
    """Set ticket by id.

    Set:
        - State - Choose what state to set the ticket to
        - Actionable - Toggle actionable

    :param pk: Ticket ID
    """
    ticket_interface = TicketCollection()

    # Show the ticket
    show_ticket_by_id(pk.strip())

    ticket = ticket_interface.get_ticket(pk.strip())
    if not ticket:
        return

    print("\nChoose the option to set (enter the number)\n\n")

    states = list(TicketState.__members__.values())

    for index, possible_state in enumerate(states, start=1):
        print(f" - {index}. {possible_state}")

    actionable_index = len(states) + 1
    ticket_actionable = ticket.actionable
    if ticket_actionable:
        print(f" - {actionable_index}. Set as not actionable\n")
    else:
        print(f" - {actionable_index}. Set as actionable\n")

    state_updated = False
    actionable_updated = False

    choice = choice_input()
    if not choice.isdigit() or int(choice) not in range(1, actionable_index + 1):
        print(f"Invalid choice {choice}, try again")
        return
    if int(choice) < actionable_index:
        state_choice = states[int(choice) - 1]
        ticket_interface.set_ticket_state(ticket.pk, state_choice)
        state_updated = True
    else:
        is_actionable = not ticket.actionable
        ticket_interface.set_ticket_actionable(ticket.pk, is_actionable)
        actionable_updated = True

    console_clear()
    # Display it after update
    show_ticket_by_id(
        pk=pk.strip(),
        state_update=state_updated,
        actionable_updated=actionable_updated,
    )


def edit_ticket_by_id(pk: str):
    """
    Edit ticket fields.

    Title [<current>]: — empty keeps (so the title can't be blanked).
    Context [<current or —>]: — a lone - clears it to "".
    Due at [<current or —>]: — a date / datetime sets it; a lone - clears it.

    :param pk: Portion of ticket ID
    :return:
    """
    ticket_interface = TicketCollection()

    ticket = ticket_interface.get_ticket(pk.strip())
    if not ticket or not isinstance(ticket, Ticket):
        print(f"No ticket found with an ID starting with {pk.strip()}")
        return

    # Show the ticket
    show_ticket_by_id(ticket.pk)
    accepted_date_formats = "(YYYY-MM-DD | YYYY-MM-DD HH:MM)"

    # Title
    title_updated = False
    title = ticket.title
    print("Update title\n - Hit enter to keep the existing title")
    choice = choice_input()
    if choice:
        title = choice
        title_updated = True

    # Context
    context_updated = False
    context = ticket.context
    print("Update context\n - Hit enter to keep the existing context\n - A bare '-' clears existing context")
    choice = choice_input()
    if choice:
        if choice == "-":
            context = ""
        else:
            context = choice
        context_updated = True

    # "Due at" & "is time-bound"
    due_at_updated = False
    new_date = ticket.due_at.strftime("%Y-%m-%d %H:%M") if ticket.due_at else None
    print("Update due\n - Hit enter to keep the existing due date"
          "\n - A bare '-' clears existing due date and sets time-bound to none\n - "
          f"Accepted Date formats: {accepted_date_formats}")
    choice = choice_input()
    option, was_updated = parse_due_input(
        raw_date_input=choice,
        allow_clear=True,
    )
    if not option and was_updated:
        new_date = None
        due_at_updated = True
    elif option and was_updated:
        new_date = option
        due_at_updated = True

    ticket = ticket_interface.edit_ticket(
        pk=ticket.pk,
        new_title=title,
        new_context=context,
        new_date=new_date,
    )
    if not ticket:
        print("Ticket update failed")
        return

    show_ticket_by_id(
        pk=ticket.pk,
        title_updated=title_updated,
        context_updated=context_updated,
        due_date_updated=due_at_updated,
    )


def main():
    """Run op"""
    parser = build_parser()
    args = parser.parse_args()

    console_clear()

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

    elif args.command == "ticket":
        if args.ticket_command == "create":
            ticket_create_dispatch(args)
        elif args.ticket_command == "list":
            list_ticket_items(args)
        elif args.ticket_command == "show":
            show_ticket_by_id(args.id)
        elif args.ticket_command == "set":
            set_ticket_by_id(args.id)
        elif args.ticket_command == "edit":
            edit_ticket_by_id(args.id)
        else:
            list_ticket_items(args)

    # Dashboard
    else:
        dashboard_data = get_dashboard_data()
        print_dashboard(dashboard_data)
