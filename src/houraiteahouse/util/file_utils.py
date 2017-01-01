from json import dumps, loads


def load_json_file(filepath):
    with open(filepath, 'r') as f:
        return loads(f.read())


def store_json_to_file(obj, filepath):
    with open(filepath, 'w') as f:
        f.write(dumps(obj))
