import json
import os

def read_mock_data():
    with open(os.path.dirname(__file__) + '/mock.json') as data_file:
        return json.load(data_file)


def list_news():
    return read_mock_data()

def get_news(postId):
    news = read_mock_data()
    for entry in news:
        if str(entry['id']) == postId:
            return entry
    return None
