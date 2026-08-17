"""Data models: structure and behaviour of data"""
import datetime

from op.storage import JsonContainer
from op.schema import Bucket, Project


class CollectionModel:
    """Base collection model"""

    def __init__(self):
        self.json_container = JsonContainer()

    def read_data(self) -> dict:
        """Read the data

        :return: The full set of data
        """
        data = self.json_container.read()
        return data

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

    def get_all_buckets(self) -> dict | None:
        """Get all buckets

        :return: Full collection of buckets
        """
        buckets = self.read_all(self.container_name)
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

        self.json_container.create(
            capture_bucket.model_dump(mode="json"),
            container_name=self.container_name
        )

    def get_bucket(self, pk: str) -> dict | None:
        """Get a bucket item by ID

        :param pk: The given ID
        :return: The bucket item or None if not found
        """
        buckets = self.get_all_buckets()
        if not buckets:
            return None
        
        for primary_key in buckets.keys():
            if primary_key.startswith(pk):
                bucket = buckets[primary_key]
                bucket['id'] = primary_key
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
        if not isinstance(bucket, dict):
            return False

        primary_key = bucket.get('id')
        data = self.read_data()
        del data['bucket'][primary_key]
        self.json_container.data = data
        self.json_container.save()

        return True


class ProjectCollection(CollectionModel):
    """Project Collection"""
    container_name = "projects"

    def count_active_projects(self) -> int:
        """Count active projects"""
        active_projects = 0
        projects = self.read_all(self.container_name)
        if not projects:
            return active_projects

        for project in projects.values():
            if project.get('state') == 'active':
                active_projects += 1

        return active_projects

    def create(self, new_project_item: dict) -> tuple[dict, str]:
        """
        Create new project

        :param new_project_item:
        :return: project and project ID
        """
        capture_project = Project.model_validate(
            {
                **new_project_item,
                "date_created": datetime.date.today(),
            }
        )
        private_key = self.json_container.create(
            capture_project.model_dump(mode="json"),
            container_name=self.container_name
        )
        projects = self.read_all(self.container_name)
        return projects[private_key], private_key


class TicketCollection(CollectionModel):
    """Ticket Collection"""
    container_name = "tickets"

    def count_active_tickets(self) -> int:
        """Count active tickets

        :return: Number of active tickets
        """
        active_tickets = 0
        tickets = self.read_all(self.container_name)
        if not tickets:
            return active_tickets

        for ticket in tickets.values():
            # Filtering will be more complicated here, but this is just stand in default for now
            if ticket.get('state') == 'active':
                active_tickets += 1

        return active_tickets


class RoutinesCollection(CollectionModel):
    """Routines/Habits Collection"""
    container_name = "habits"

    def count_active_habits(self) -> int:
        """Count active habits

        :return: Number of active routines
        """
        active_habits = 0
        habits = self.read_all(self.container_name)
        if not habits:
            return active_habits

        for habit in habits.values():
            # Filtering will be more complicated here, but this is just stand in default for now
            if habit.get('state') == 'active':
                active_habits += 1

        return active_habits
