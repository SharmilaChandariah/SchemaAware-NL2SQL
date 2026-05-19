
from pathlib import Path

def load_schema(path):
    return Path(path).read_text()
