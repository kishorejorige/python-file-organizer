import argparse
from pathlib import Path

from organizer.config import load_config
from organizer.logger import setup_logger
from organizer.engine import rules as rules_module
from organizer.engine.organizer import OrganizerEngine
from organizer.watcher import watch_folder


def build_parser():
    parser = argparse.ArgumentParser(
        prog="file-organizer",
        description="Organize files into folders based on file type"
    )

    parser.add_argument(
        "path",
        help="Folder path to organize"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving files"
    )

    parser.add_argument(
        "--log-file",
        default="logs/organizer.log",
        help="Path to log file"
    )
    
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Watch folder and auto-organize"
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    cfg = load_config("config.json")
    # CLI flags override config
    if args.dry_run:
        cfg["dry_run"] = True
    if args.watch:
        cfg["watch"] = True

    logger = setup_logger(args.log_file)

    # load rules
    defaults = rules_module.load_default_rules()
    customs = []
    rules_file = cfg.get("rules_file")
    if rules_file:
        # if relative path, resolve relative to package rules dir or current cwd
        p = Path(rules_file)
        if not p.exists():
            # try package rules
            pkg = Path(__file__).parent / "rules" / Path(rules_file).name
            if pkg.exists():
                customs = rules_module.load_custom_rules(str(pkg))
        else:
            customs = rules_module.load_custom_rules(str(p))

    rules = rules_module.merge_rules(defaults, customs)

    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    root = Path(args.path)
    if cfg.get("watch"):
        watch_folder(str(root), engine, dry_run=cfg.get("dry_run", False))
        return

    engine.run(root, dry_run=cfg.get("dry_run", False))


if __name__ == "__main__":
    main()