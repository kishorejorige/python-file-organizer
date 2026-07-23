"""Compatibility wrapper for loading rules.

Deprecated: use organizer.engine.rules directly for advanced usage.
"""

from organizer.engine import rules as rules_module
from organizer.config import load_config
from pathlib import Path


def load_rules(config_path: str = "config.json"):
    cfg = load_config(config_path)
    defaults = rules_module.load_default_rules()
    customs = []
    rf = cfg.get("rules_file")
    if rf:
        p = Path(rf)
        if p.exists():
            customs = rules_module.load_custom_rules(str(p))
        else:
            # try package rules folder
            pkg = Path(__file__).parent / "rules" / Path(rf).name
            if pkg.exists():
                customs = rules_module.load_custom_rules(str(pkg))

    return rules_module.merge_rules(defaults, customs)
