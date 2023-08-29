import json


class FileHandler:
    def __init__(self, name):
        self.name = name

    def read_file(self):
        with open(self.name, 'r') as file:
            return json.loads(file)

    @staticmethod
    def write_file(name, data):
        with open(name, 'w') as file:
            json.dumps(data, file)