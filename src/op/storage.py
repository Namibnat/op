"""The data connection interface"""

import json
import os
from pathlib import Path

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

    def save(self):
        """Save container"""
        with open(self.planner, 'w') as fs:
            json.dump(self.data, fs, indent=2)

    def read(self) -> dict:
        """Read data

        :return: full data object
        """
        if not os.path.exists(self.planner):
            self._create_container()
        with open(self.planner) as fs:
            self.data = json.load(fs)
            self._validate_structure()
            return self.data
