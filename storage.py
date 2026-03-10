# Storage Manager

from pathlib import Path
import json

from url_entity import URL

BASE_DIR = Path(__file__).parent


# Low level Handler
class JSONFile:

    def __init__(self, file_name):
        self.file_path = self.create(file_name)

    def create(self, file_name):

        path = BASE_DIR / file_name
        if not path.exists():
            with open(path, "w") as f:
                json.dump([], f, indent=4)
        return path

    def read_all(self):

        with open(self.file_path, "r") as f:

            data = json.load(f)
            return data

    def write_all(self, data):

        with open(self.file_path, "w") as f:

            json.dump(data, f, indent=4)


class URLDB:

    def __init__(self, url_file="urls.json"):
        self.json_handler = JSONFile(url_file)

    def add(self, url: URL):

        data = self.json_handler.read_all()

        url_dict = url.to_dict()

        data.append(url_dict)

        self.json_handler.write_all(data)

    def find_by_url(self, long_url):

        data = self.json_handler.read_all()

        url_obj = None
        for url_dict in data:
            if url_dict["long_url"] == long_url:
                url_obj = URL.from_dict(url_dict)
                break

        return url_obj

    def find_by_code(self, short_code):

        data = self.json_handler.read_all()

        url_obj = None
        for url_dict in data:
            if url_dict["short_code"] == short_code:
                url_obj = URL.from_dict(url_dict)
                break

        return url_obj

    def list_all(self) -> list[URL]:

        data = self.json_handler.read_all()

        for i, url_dict in enumerate(data):
            data[i] = URL.from_dict(url_dict)

        return data

    def update(self, url: URL) -> bool:

        data = self.json_handler.read_all()

        updated = False
        for i, url_dict in enumerate(data):
            if url_dict["url_id"] == url.url_id:
                data[i] = url.to_dict()
                updated = True
                break

        self.json_handler.write_all(data)

        return updated

    def delete(self, url: URL) -> bool:

        data = self.json_handler.read_all()

        filtered = [url_dict for url_dict in data if url_dict["url_id"] != url.url_id]

        if len(data) == len(filtered):
            return False

        self.json_handler.write_all(filtered)
        return True
