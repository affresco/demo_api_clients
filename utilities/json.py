from typing import Dict

try:
    import ujson as json
except:
    import json


def loads(data):
    if isinstance(data, list):
        return data
    if isinstance(data, Dict):
        return data
    try:
        return json.loads(data)
    except:
        return data


def dumps(data):
    if isinstance(data, bytes):
        return data
    if isinstance(data, bytearray):
        return data
    try:
        return json.dumps(data)
    except:
        return data