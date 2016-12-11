from json import dumps, loads


def load_json_file(filepath):
    f = open(filepath, 'r')
    raw = f.read()
    f.close()
    return loads(raw)


def store_json_to_file(obj, filepath):
    f = open(filepath, 'w')
    f.write(dumps(obj))
    f.close()
