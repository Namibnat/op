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
DATA_DIR = Path()


class JsonContainer:
    """Container data connection interface"""
    filename = 'planner.json'

    def __init__(self):
        self.bucket = DATA_DIR / self.filename
        self.data = BASE_STRUCTURE

    def _validate_structure(self):
        """Validate the data structure in the file"""
        if not isinstance(self.data, dict):
            raise ValueError("The structure of the planner.json file is not valid")

        for container_name in BASE_STRUCTURE.keys():
            if not container_name in self.data.keys():
                raise ValueError(f"Container missing top level key: {container_name}")

    def _create_container(self):
        """Create new container as needed"""
        with open(self.bucket, 'w') as fs:
            json.dump(BASE_STRUCTURE, fs)

    def _read_container(self):
        """Read data"""
        with open(self.bucket) as fs:
            self.data = json.load(fs)
            self._validate_structure()

    def read_bucket(self):
        """Read bucket data"""
        if not self.filename in os.listdir(DATA_DIR):
            self._create_container()
        self._read_container()
