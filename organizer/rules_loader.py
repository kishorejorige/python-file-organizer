import json
from pathlib import Path


def load_rules(config_path="config.json"):
    path = Path(config_path)

    if not path.exists():
        raise FileNotFoundError("config.json not found")

    with open(path, "r") as f:
        data = json.load(f)

    return data.get("rules", [])
