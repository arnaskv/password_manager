import json


class FileHandler:
    def __init__(self, filename):
        self.name = filename

    def read_json(self):
        try:
            with open(self.name, 'r') as file:
                data = json.loads(file)
            return data
        except FileNotFoundError:
            print(f'File "{self.filename} not found."')
            return None
        except json.JSONDecodeError:
            print(f'Error decoding JSON in "{self.filename}"')
            return None

    def write_json(self, data):
        try:
            with open(self.filename, 'w') as file:
                json.dumps(data, file)
                print(f'Data successfully written to "{self.filename}"')
        except Exception as e:
            print(f'Error writing to "{self.filename}" : {str(e)}')
