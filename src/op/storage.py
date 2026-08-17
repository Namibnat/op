"""The data connection interface"""

import json
import os
from pathlib import Path
import uuid

from dotenv import load_dotenv

from op.config import BASE_STRUCTURE

load_dotenv()
data_dir = os.getenv('OP_DATA_DIR')
if not data_dir:
    raise ValueError("No data directory provided")
DATA_DIR = Path(data_dir).expanduser()


class JsonContainer:
    """Container data connection interface"""
    filename = 'planner.json'
    data = BASE_STRUCTURE

    def __init__(self):
        self.planner = DATA_DIR / self.filename

    def _validate_structure(self):
        """Validate the data structure in the file"""
        if not isinstance(self.data, dict):
            raise ValueError("The structure of the planner.json file is not valid")

        for container_name in BASE_STRUCTURE.keys():
            if not container_name in self.data.keys():
                raise ValueError(f"Container missing top level key: {container_name}")

    def _create_container(self):
        """Create new container as needed"""
        with open(self.planner, 'w') as fs:
            json.dump(BASE_STRUCTURE, fs)

    def _save_container(self):
        """Save container"""
        with open(self.planner, 'w') as fs:
            json.dump(self.data, fs, indent=2)

    def _read_container(self):
        """Read data

        :return: full data object
        :rtype: dict
        """
        with open(self.planner) as fs:
            self.data = json.load(fs)

            self._validate_structure()

            return self.data

    def read(self):
        """Read data

        :return: full data object
        :rtype: dict
        """
        if not self.planner.exists():
            self._create_container()

        return self._read_container()

    def create(self, new_item: dict, container_name: str) -> str:
        """Create a new field in one of the containers

        :param new_item: The new item to be added
        :param container_name: Which container it should go to.
        :return: Private key
        :rtype: str
        """
        self.data = self.read()
        if container_name not in self.data:
            raise ValueError(f"No container named {container_name} exists")

        private_key = str(uuid.uuid4())

        self.data[container_name][private_key] = new_item
        self._save_container()

        return private_key

    def save(self):
        """Save data"""
        self._save_container()
