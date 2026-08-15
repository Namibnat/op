"""Data models: structure and behaviour of data"""

from op.storage import JsonContainer


class CollectionModel:
    json_container = JsonContainer()

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

    @classmethod
    def _validate(cls):
        pass

    def count_all_buckets(self):
        """Count all buckets

        :return: Number of buckets
        :rtype: int
        """
        buckets = self.read_all(self.container_name)
        return len(buckets)

    @classmethod
    def create(cls):
        pass


class ProjectCollection(CollectionModel):
    container_name = "projects"

    @classmethod
    def _validate(cls):
        pass

    def count_active_projects(self):
        """TODO: UPDATE DOCSTRING"""
        active_projects = 0
        projects = self.read_all(self.container_name)
        if not projects:
            return active_projects

        for project in projects.values():
            if project.get('state') == 'active':
                active_projects += 1

        return active_projects
