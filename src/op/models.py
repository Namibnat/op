"""Data models: structure and behaviour of data"""
import datetime
from typing import List

from op.schema import Bucket, Project, ProjectState, ProjectResource, TicketState, Ticket
from op.storage import JsonContainer


class CollectionModel:
    """Base collection model"""

    def __init__(self):
        self.json_container = JsonContainer()
        self.data: dict = self.read_data()

    def read_data(self) -> dict:
        """Read the data

        :return: The full set of data
        """
        self.data = self.json_container.read()
        return self.data

    def save_data(self):
        self.json_container.data = self.data
        self.json_container.save()

    def read_all(self, container_name: str) -> dict | None:
        """Read all container entries

        :param container_name: container name
        :return: all container objects
        """
        data = self.read_data()
        container = data.get(container_name)
        if container is None:
            return None
        if not isinstance(container, dict):
            raise TypeError(f"Found object of type {type(container)}")
        return container


class BucketCollection(CollectionModel):
    """Bucket Collection Model"""
    container_name = "bucket"

    def get_all_buckets(self) -> list[Bucket] | None:
        """Get all buckets

        :return: Full collection of buckets
        """
        stored_buckets = self.read_all(self.container_name)
        if not stored_buckets:
            return None

        buckets = list()
        for pk, bucket_item in stored_buckets.items():
            buckets.append(Bucket.model_validate({'pk': pk, **bucket_item}))
        return buckets

    def count_all_buckets(self) -> int:
        """Count all buckets

        :return: Number of buckets
        """
        buckets = self.get_all_buckets()
        if not buckets:
            return 0
        return len(buckets)

    def create(self, new_bucket_item: str):
        """Add a new item to the collection bucket"""
        capture_bucket = Bucket.model_validate(
            {
                "item": new_bucket_item,
                "date_created": datetime.date.today()
            }
        )
        bucket_data = capture_bucket.model_dump(mode="json", exclude={"pk"})

        self.data[self.container_name][capture_bucket.pk] = bucket_data
        self.save_data()

    def get_bucket(self, pk: str) -> Bucket | None:
        """Get a bucket item by ID

        :param pk: The given ID
        :return: The bucket item or None if not found
        """
        buckets = self.get_all_buckets()
        if not buckets:
            return None

        for bucket in buckets:
            if bucket.pk.startswith(pk):
                return bucket

        return None

    def discard_bucket(self, pk: str) -> bool:
        """Discard a bucket item by ID

        The idea is that bucket items are cheap, just ideas.
        So discarding isn't high-friction and no archives.

        :param pk: The given ID
        :return: Delete success status, True if delete successful
        """
        bucket = self.get_bucket(pk)
        if not isinstance(bucket, Bucket):
            return False

        data = self.read_data()

        del data['bucket'][bucket.pk]
        self.json_container.data = data
        self.save_data()

        return True


class ProjectCollection(CollectionModel):
    """Project Collection"""
    container_name = "projects"

    @staticmethod
    def create_project_models(data_projects: dict) -> list[Project] | None:
        """Expand dict of projects into list of project models

        :param data_projects: Projects in the store form
        :return: List of project models
        """
        projects = list()
        if not data_projects:
            return None

        for key, value in data_projects.items():
            projects.append(
                Project.model_validate(
                    {'pk': key,
                     **value
                     }
                )
            )
        return projects

    def count_active_projects(self) -> int:
        """Count active projects"""
        active_projects = 0
        data_projects = self.read_all(self.container_name)
        if not data_projects:
            return active_projects

        projects = self.create_project_models(data_projects)
        if not projects:
            return active_projects

        for project in projects:
            if project.state == 'active':
                active_projects += 1

        return active_projects

    def create(self, new_project_item: Project) -> Project:
        """
        Create new project

        :param new_project_item: Project instance to create
        :return: project
        """
        data_project = new_project_item.model_dump(mode="json", exclude={"pk"})
        self.data[self.container_name][new_project_item.pk] = data_project
        self.save_data()

        return new_project_item

    def get_all_projects(self) -> list[Project]:
        """Get all projects

        :return: all projects
        """
        data_projects = self.read_all(self.container_name)

        projects = list()

        if not data_projects:
            return projects

        all_projects = self.create_project_models(data_projects)
        if all_projects:
            return all_projects
        return projects

    def get_filtered_projects(self, project_filter: str) -> list | None:
        """Get filtered projects

        :param project_filter: Project filter
        :return: Projects, filtered by filter
        """
        data_projects = self.get_all_projects()
        if not isinstance(data_projects, list):
            return None

        if project_filter == 'all':
            return data_projects

        project_filter = 'not_started' if project_filter == 'new' else project_filter
        filtered_projects = list()
        for project in data_projects:
            if project.state == project_filter:
                filtered_projects.append(project)

        return filtered_projects

    def get_project(self, pk: str) -> Project | None:
        """Show project by ID

        :param pk: project ID
        :return: A single project or None
        """
        projects = self.get_all_projects()
        if not isinstance(projects, list):
            return None

        for project in projects:
            if project.pk.startswith(pk):
                return project

        return None

    def _save_data_with_project(self, project: Project):
        """Add project to store format and save data

        :param project: The project to save
        """
        data_project = project.model_dump(
            mode="json",
            exclude={"pk": True, 'resources': {"__all__": {"pk": True}}}
        )
        self.data[self.container_name][project.pk] = data_project
        self.save_data()

    def set_project_state(self, pk: str, state: ProjectState) -> Project | None:
        """Set the state of a project given by its ID

        :param pk: Project ID
        :param state: New state
        :return: A single project or None
        """
        project = self.get_project(pk)
        if not isinstance(project, Project):
            return None

        project.state = state
        self._save_data_with_project(project)
        return project

    def add_project_resource(self, pk: str, resource: ProjectResource) -> Project | None:
        """Add a project resource

        :param pk: Project ID
        :param resource: New resource to be added to a project.
        :return: Project after resource update, None if there is no valid project
        """
        project = self.get_project(pk)
        if not project:
            return None

        project.resources[resource.pk] = resource
        self._save_data_with_project(project)

        project = self.get_project(pk)
        return project

    def delete_project_resource(self, project_pk: str, resource_pk: str) -> bool:
        """Remove a resource item

        :param project_pk: Project ID
        :param resource_pk: Partial resource ID
        :return: Delete success
        """
        project = self.get_project(project_pk)
        if not project:
            return False

        remove_key = None
        resources = project.resources
        for key, value in resources.items():
            if key.startswith(resource_pk):
                remove_key = key
                break

        if remove_key:
            del resources[remove_key]
            self._save_data_with_project(project)
            return True

        return False


class TicketCollection(CollectionModel):
    """Ticket Collection"""
    container_name = "tickets"

    @staticmethod
    def create_ticket_models(data_tickets: dict) -> list[Ticket] | None:
        """Expand dict of tickets into list of tickets models

        :param data_tickets: Tickets in the store form
        :return: List of ticket models
        """
        tickets = list()
        if not data_tickets:
            return None

        for key, value in data_tickets.items():
            tickets.append(
                Ticket.model_validate(
                    {'pk': key,
                     **value
                     }
                )
            )
        return tickets

    def _save_data_with_ticket(self, ticket: Ticket):
        """Add ticket to store format and save data

        :param ticket: The ticket to save
        """
        data_project = ticket.model_dump(
            mode="json",
            exclude={"pk": True, 'resources': {"__all__": {"pk": True}}}
        )
        self.data[self.container_name][ticket.pk] = data_project
        self.save_data()

    def count_active_tickets(self) -> int:
        """Count active tickets

        :return: Number of active tickets
        """
        active_tickets = 0

        data_tickets = self.read_all(self.container_name)
        if not data_tickets:
            return active_tickets

        active_tickets = len(data_tickets)
        return active_tickets

    def create(self, new_ticket_item: Ticket) -> Ticket:
        """Create a new ticket

        :param new_ticket_item: The ticket being created.
        :return: The ticket after creation
        """
        data_ticket = new_ticket_item.model_dump(mode="json", exclude={"pk"})
        self.data[self.container_name][new_ticket_item.pk] = data_ticket

        self.save_data()

        return new_ticket_item

    def get_all_tickets(self) -> list[Ticket] | None:
        """Get all tickets

        :return: List of all tickets or None
        """
        data_tickets = self.read_all(self.container_name)
        if not data_tickets:
            return None

        all_tickets = self.create_ticket_models(data_tickets)
        if not all_tickets:
            return None

        all_tickets = [t for t in all_tickets if not t.state == TicketState.CANCELLED]

        return all_tickets

    def get_ticket(self, pk: str) -> Ticket | None:
        """Get a ticket by its ID

        :param pk: Ticket ID
        :return: Ticket or None
        """
        all_tickets = self.get_all_tickets()
        if not all_tickets:
            return None
        for ticket in all_tickets:
            if ticket.pk.startswith(pk):
                return ticket

        return None

    def get_project_tickets(self, pk: str) -> List[Ticket] | None:
        """Get all tickets for a project.

        :param pk: Project ID
        :return: List of tickets
        """
        all_tickets = self.get_all_tickets()
        if not all_tickets:
            return None

        project_tickets = []

        for ticket in all_tickets:
            if not ticket.project:
                continue

            if ticket.project.startswith(pk):
                project_tickets.append(ticket)

        return project_tickets

    def get_tickets_by_state(self, state: str) -> list[Ticket] | None:
        """Get all tickets for a state

        :param state: State
        :return: List of tickets
        """
        all_tickets = self.get_all_tickets()
        if not all_tickets:
            return None

        filtered_tickets = []
        for ticket in all_tickets:
            if ticket.state == state:
                filtered_tickets.append(ticket)

        return filtered_tickets

    def get_actionable_tickets(self) -> list[Ticket] | None:
        """Get all actionable tickets

        :return: List of actionable tickets
        """
        all_tickets = self.get_all_tickets()
        if not all_tickets:
            return None
        filtered_tickets = []
        for ticket in all_tickets:
            if ticket.actionable:
                filtered_tickets.append(ticket)
        return filtered_tickets

    def set_ticket_state(self, pk: str, state: TicketState) -> Ticket | None:
        """Set state for a ticket.

        :param pk: Ticket ID
        :param state: State
        """
        ticket = self.get_ticket(pk)
        if not isinstance(ticket, Ticket):
            return None

        if ticket.state == state:
            return ticket

        # If switching from "done", completed also needs to be reset.
        if ticket.state == TicketState.DONE:
            ticket.date_completed = None

        ticket.state = state

        if ticket.state == TicketState.DONE:
            ticket.date_completed = datetime.date.today()

        self._save_data_with_ticket(ticket)
        return ticket

    def set_ticket_actionable(self, pk: str, actionable: bool) -> Ticket | None:
        """Set actionable state for a ticket.

        :param pk: Ticket ID
        :param actionable: Actionable
        """
        ticket = self.get_ticket(pk)
        if not isinstance(ticket, Ticket):
            return None

        if ticket.actionable == actionable:
            return ticket

        ticket.actionable = actionable
        self._save_data_with_ticket(ticket)

        return ticket

    def edit_ticket(
            self,
            pk: str,
            new_title: str | None,
            new_context: str | None,
            new_date: str | None,
    ) -> Ticket | None:
        """Edit ticket

        :param pk: Ticket ID
        :param new_title: New title if updated
        :param new_context: New context if updated
        :param new_date: New date if updated.  Will set time-bound if not set.
        :return: Ticket or None
        """
        ticket = self.get_ticket(pk)
        if not isinstance(ticket, Ticket):
            return None

        data = ticket.model_dump(mode="json")
        data["title"] = new_title
        data["context"] = new_context
        data["due_at"] = new_date
        data["time_bound"] = new_date is not None

        updated_ticket = Ticket.model_validate(data)

        self._save_data_with_ticket(updated_ticket)

        return updated_ticket


class RoutinesCollection(CollectionModel):
    """Routines/Habits Collection"""
    container_name = "habits"

    @staticmethod
    def count_active_habits() -> int:
        """Count active habits

        :return: Number of active routines
        """
        active_habits = 0
        return active_habits
