import json
import warnings
from pathlib import Path
from typing import Dict, Union

# keep FILE_TYPES constant for tests and compatibility
FILE_TYPES = {
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".tiff",
        ".ico",
        ".heic",
        ".psd",
        ".ai",
        ".eps",
        ".indd",
        ".raw",
        ".nef",
        ".cr2",
        ".orf",
        ".sr2",
        ".dng",
    ],
    "Documents": [
        ".pdf",
        ".docx",
        ".txt",
        ".xlsx",
        ".pptx",
        ".odt",
        ".ods",
        ".odp",
        ".rtf",
        ".csv",
        ".md",
        ".tex",
    ],
    "Videos": [
        ".mp4",
        ".mkv",
        ".avi",
        ".mov",
        ".wmv",
        ".flv",
        ".webm",
        ".mpeg",
        ".mpg",
        ".3gp",
    ],
    "Audio": [
        ".mp3",
        ".wav",
        ".flac",
        ".aac",
        ".m4a",
    ],
}


DEFAULT_CONFIG = {
    "dry_run": False,
    "recursive": True,
    "watch": False,
    "ignore_dirs": [".git", "__pycache__", "node_modules"],
    "rules_file": "rules/default_rules.json",
}


class ConfigError(ValueError):
    """Raised when a config file exists but cannot be loaded or is invalid."""


def load_config(
    path: Union[str, Path] = "config.json", *, strict: bool = False
) -> Dict:
    p = Path(path)
    if not p.exists():
        if strict:
            raise FileNotFoundError(f"Config file not found: {p}")
        return DEFAULT_CONFIG.copy()

    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        message = f"Could not load config file '{p}': {exc}"
        if strict:
            raise ConfigError(message) from exc
        warnings.warn(message, RuntimeWarning, stacklevel=2)
        return DEFAULT_CONFIG.copy()
    except Exception as exc:
        message = f"Could not load config file '{p}': {exc}"
        if strict:
            raise ConfigError(message) from exc
        warnings.warn(message, RuntimeWarning, stacklevel=2)
        return DEFAULT_CONFIG.copy()

    if not isinstance(data, dict):
        message = f"Config file '{p}' must contain a JSON object."
        if strict:
            raise ConfigError(message)
        warnings.warn(message, RuntimeWarning, stacklevel=2)
        return DEFAULT_CONFIG.copy()

    cfg = DEFAULT_CONFIG.copy()

    # Validate keys and types
    expected_types = {
        "dry_run": bool,
        "recursive": bool,
        "watch": bool,
        "ignore_dirs": list,
        "rules_file": str,
    }

    for key, expected_type in expected_types.items():
        if key in data:
            val = data[key]
            if not isinstance(val, expected_type):
                message = f"Config key '{key}' must be of type {expected_type.__name__}, got {type(val).__name__}."
                if strict:
                    raise ConfigError(message)
                warnings.warn(message, RuntimeWarning, stacklevel=2)
                continue

            if expected_type is list:
                if not all(isinstance(item, str) for item in val):
                    message = "All items in ignore_dirs must be strings."
                    if strict:
                        raise ConfigError(message)
                    warnings.warn(message, RuntimeWarning, stacklevel=2)
                    continue

            cfg[key] = val

    return cfg
