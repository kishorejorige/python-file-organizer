import json
import pkgutil
from pathlib import Path
from typing import List, Dict


def validate_rules(rules: List[Dict]):
    if not isinstance(rules, list):
        raise ValueError("Rules must be a list of dictionaries.")
    for index, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule at index {index} must be a dictionary.")
        if "folder" not in rule:
            raise ValueError(f"Rule at index {index} is missing required key 'folder'.")
        if "extensions" not in rule:
            raise ValueError(
                f"Rule at index {index} is missing required key 'extensions'."
            )

        folder = rule["folder"]
        extensions = rule["extensions"]

        if not isinstance(folder, str) or not folder.strip():
            raise ValueError(
                f"Rule at index {index} 'folder' must be a non-empty string."
            )

        # Path traversal prevention: prevent folder name from escaping the root directory
        if ".." in folder or "/" in folder or "\\" in folder:
            raise ValueError(
                f"Rule at index {index} 'folder' contains invalid characters or path traversal elements ('..', '/', '\\')."
            )

        if not isinstance(extensions, list) or not all(
            isinstance(ext, str) for ext in extensions
        ):
            raise ValueError(
                f"Rule at index {index} 'extensions' must be a list of strings."
            )

        for ext in extensions:
            if not isinstance(ext, str) or not ext.startswith("."):
                raise ValueError(
                    f"Rule at index {index} extension '{ext}' must be a string starting with a '.'"
                )


def load_default_rules() -> List[Dict]:
    # Try to load packaged data (works inside zipapps, PyInstaller bundles, etc.)
    rules = []
    try:
        data = pkgutil.get_data("organizer", "rules/default_rules.json")
        if data:
            rules = json.loads(data.decode("utf-8"))
    except Exception:  # nosec B110
        pass

    if not rules:
        # Fallback to file on disk (useful for local development)
        pkg_rules = Path(__file__).parent.parent / "rules" / "default_rules.json"
        if pkg_rules.exists():
            with open(pkg_rules, "r", encoding="utf-8") as f:
                rules = json.load(f)

    if rules:
        validate_rules(rules)
    return rules


def load_custom_rules(path: str) -> List[Dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Rules file not found at: {p}")
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in rules file '{p}': {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Could not read rules file '{p}': {exc}") from exc

    rules = data.get("rules", []) if isinstance(data, dict) else data
    validate_rules(rules)
    return rules


def merge_rules(defaults: List[Dict], customs: List[Dict]) -> List[Dict]:
    # customs override default by folder name; simple replacement
    merged = {r["folder"]: r for r in defaults}
    for r in customs:
        merged[r["folder"]] = r
    return list(merged.values())


def find_category_for_extension(rules: List[Dict], extension: str) -> str:
    ext = extension.lower()
    for rule in rules:
        exts = [e.lower() for e in rule.get("extensions", [])]
        if ext in exts:
            return rule.get("folder", "Others")
    return "Others"
