import json
from pathlib import Path
from typing import Dict

# keep FILE_TYPES constant for tests and compatibility
FILE_TYPES = {
    "Images": [
        ".jpg", ".jpeg", ".png", ".gif", ".bmp",
        ".svg", ".webp", ".tiff", ".ico", ".heic",
        ".psd", ".ai", ".eps", ".indd", ".raw",
        ".nef", ".cr2", ".orf", ".sr2", ".dng",
    ],
    "Documents": [
        ".pdf", ".docx", ".txt", ".xlsx", ".pptx",
        ".odt", ".ods", ".odp", ".rtf", ".csv",
        ".md", ".tex",
    ],
    "Videos": [
        ".mp4", ".mkv", ".avi", ".mov", ".wmv",
        ".flv", ".webm", ".mpeg", ".mpg", ".3gp",
    ],
    "Audio": [
        ".mp3", ".wav", ".flac", ".aac", ".m4a",
    ],
}


DEFAULT_CONFIG = {
    "dry_run": False,
    "recursive": True,
    "watch": False,
    "ignore_dirs": [".git", "__pycache__", "node_modules"],
    "rules_file": "rules/default_rules.json",
}


def load_config(path: str = "config.json") -> Dict:
    p = Path(path)
    if not p.exists():
        return DEFAULT_CONFIG.copy()
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = DEFAULT_CONFIG.copy()
        cfg.update(data)
        return cfg
    except Exception:
        return DEFAULT_CONFIG.copy()
