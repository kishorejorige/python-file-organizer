"""Orchestration helper for organizer package.

This module intentionally contains no CLI logic. Use `organizer.cli` as the
command-line entrypoint which uses classes from `organizer.engine`.
"""

from pathlib import Path
from organizer.engine.organizer import OrganizerEngine


def run(root_path: str, engine: OrganizerEngine):
    root = Path(root_path)
    return engine.run(root, dry_run=engine.config.get("dry_run", False))


def main():
    """Minimal main for compatibility with tests and packaging.

    Real CLI entrypoint is organizer.cli:main
    """
    return None