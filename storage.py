# Storage Manager

from pathlib import Path
import json

BASE_DIR = Path(__file__).parent


# Low level Handler
class JSONFile:

    def __init__(self, file_name):
        self.file_path = self.create(file_name)

    def create(self, file_name):

        path = BASE_DIR / file_name
        if not path.exist():
            with open(path, "w") as f:
                json.dump({}, f, indent=4)
        return path

    def read_all(self):

        with open(self.file_path, "r") as f:

            data = json.load(f)
            return data

    def write_all(self, data):

        with open(self.file_path, "w") as f:

            json.dump(data, f, indent=4)


class URLDB:

    pass
