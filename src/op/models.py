"""Data models: structure and behaviour of data"""
import datetime
from op.config import DATE_STR_FORM

from op.storage import JsonContainer


def date_day_string():
    """Create a formatted date string for printing

    :return: Formatted date string
    :rtype: str
    """
    date = datetime.datetime.now()
    return date.strftime(DATE_STR_FORM)


class CollectionModel:

    def __init__(self):
        self.json_container = JsonContainer()

    def read_data(self):
        """Read the data

        :return: The full set of data
        :rtype: dict
        """
        data = self.json_container.read()
        return data

    def read_all(self, container_name):
        """Read all container entries

        :param container_name: container name
        :return: all bucket objects
        :rtype: dict
        """
        data = self.read_data()
        projects = data.get(container_name)
        return projects


class BucketCollection(CollectionModel):
    container_name = "bucket"

    def get_all_buckets(self):
        """Get all buckets"""
        buckets = self.read_all(self.container_name)
        return buckets

    def count_all_buckets(self):
        """Count all buckets

        :return: Number of buckets
        :rtype: int
        """
        buckets = self.get_all_buckets()
        return len(buckets)

    def create(self, new_bucket_item):
        """Add a new item to the collection bucket"""
        capture_bucket = {
            "item": new_bucket_item,
            "date_created": date_day_string(),
            "status": "fresh"
        }
        self.json_container.create(
            capture_bucket,
            container_name=self.container_name
        )

    def get_bucket(self, pk):
        """Get a bucket item by ID

        :param pk: The given ID
        :return: The bucket item or None if not found
        :rtype: dict or None
        """
        buckets = self.get_all_buckets()
        bucket_keys = buckets.keys()
        for primary_key in bucket_keys:
            if primary_key.startswith(pk):
                bucket = buckets[primary_key]
                bucket['id'] = primary_key
                return bucket
        return None


class ProjectCollection(CollectionModel):
    """Project Collection"""
    container_name = "projects"

    def count_active_projects(self):
        """Count active projects"""
        active_projects = 0
        projects = self.read_all(self.container_name)
        if not projects:
            return active_projects

        for project in projects.values():
            if project.get('state') == 'active':
                active_projects += 1

        return active_projects

    def create(self):
        pass


class TicketCollection(CollectionModel):
    """Ticket Collection"""
    container_name = "tickets"

    def count_active_tickets(self):
        """Count active tickets"""
        active_tickets = 0
        tickets = self.read_all(self.container_name)
        if not tickets:
            return active_tickets

        for ticket in tickets.values():
            # Filtering will be more complicated here, but this is just stand in default for now
            if ticket.get('state') ==  'active':
                active_tickets += 1

        return active_tickets


class RoutinesCollection(CollectionModel):
    """Routines/Habits Collection"""
    container_name = "habits"

    def count_active_habits(self):
        """Count active habits"""
        active_habits = 0
        habits = self.read_all(self.container_name)
        if not habits:
            return active_habits

        for habit in habits.values():
            # Filtering will be more complicated here, but this is just stand in default for now
            if habit.get('state') ==  'active':
                active_habits += 1

        return active_habits
