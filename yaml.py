import json

def safe_load(stream):
    if hasattr(stream, 'read'):
        stream = stream.read()
    return json.loads(stream)
