import argparse
import logging
import sys
from pathlib import Path

from organizer.config import ConfigError, load_config
from organizer.logger import setup_logger
from organizer.engine import rules as rules_module
from organizer.engine.organizer import OrganizerEngine
from organizer.watcher import watch_folder


def build_parser():
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Organize files into folders based on file type",
    )

    parser.add_argument("path", help="Folder path to organize")

    parser.add_argument("--config", default="config.json", help="Path to config file")

    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without moving files"
    )

    parser.add_argument(
        "--log-file", default="logs/organizer.log", help="Path to log file"
    )

    parser.add_argument(
        "--watch", action="store_true", help="Watch folder and auto-organize"
    )

    parser.add_argument(
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="Scan subfolders recursively",
    )

    parser.add_argument("--rules-file", help="Path to a custom rules JSON file")

    parser.add_argument(
        "--ignore-dir",
        action="append",
        dest="ignore_dirs",
        default=[],
        help="Directory name to ignore; can be used more than once",
    )

    parser.add_argument(
        "--verbose", action="store_true", help="Show more detailed log output"
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config, strict=True)
    except Exception as exc:
        parser.error(str(exc))

    # CLI flags override config
    if args.dry_run:
        cfg["dry_run"] = True
    if args.watch:
        cfg["watch"] = True
    if args.recursive is not None:
        cfg["recursive"] = args.recursive
    if args.rules_file:
        cfg["rules_file"] = args.rules_file
    if args.ignore_dirs:
        cfg["ignore_dirs"] = list(cfg.get("ignore_dirs", [])) + args.ignore_dirs

    log_level = logging.DEBUG if args.verbose else logging.INFO
    try:
        logger = setup_logger(args.log_file, level=log_level)
    except Exception as exc:
        print(f"Error setting up logger: {exc}", file=sys.stderr)
        sys.exit(1)

    root = Path(args.path)
    if not root.exists():
        print(f"Error: Root path '{root}' does not exist.", file=sys.stderr)
        sys.exit(1)
    if not root.is_dir():
        print(f"Error: Root path '{root}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    # load rules
    try:
        defaults = rules_module.load_default_rules()
        customs = []
        rules_file = cfg.get("rules_file")
        if rules_file:
            p = Path(rules_file)
            if not p.exists():
                pkg = Path(__file__).parent / "rules" / Path(rules_file).name
                if pkg.exists():
                    customs = rules_module.load_custom_rules(str(pkg))
                else:
                    raise ConfigError(f"Rules file '{rules_file}' not found.")
            else:
                customs = rules_module.load_custom_rules(str(p))

        rules = rules_module.merge_rules(defaults, customs)
    except Exception as exc:
        print(f"Error loading configuration rules: {exc}", file=sys.stderr)
        sys.exit(1)

    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    try:
        if cfg.get("watch"):
            watch_folder(str(root), engine, dry_run=cfg.get("dry_run", False))
            return 0

        engine.run(root, dry_run=cfg.get("dry_run", False))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
