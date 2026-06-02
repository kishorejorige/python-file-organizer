import json
import pkgutil
from pathlib import Path
from typing import List, Dict


def load_default_rules() -> List[Dict]:
    # Try to load packaged data (works inside zipapps, PyInstaller bundles, etc.)
    try:
        data = pkgutil.get_data("organizer", "rules/default_rules.json")
        if data:
            return json.loads(data.decode("utf-8"))
    except Exception:
        pass

    # Fallback to file on disk (useful for local development)
    pkg_rules = Path(__file__).parent.parent / "rules" / "default_rules.json"
    if not pkg_rules.exists():
        return []
    with open(pkg_rules, "r", encoding="utf-8") as f:
        return json.load(f)


def load_custom_rules(path: str) -> List[Dict]:
    p = Path(path)
    if not p.exists():
        return []
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("rules", []) if isinstance(data, dict) else data


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
