import argparse
from organizer.main import run_organizer


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


def main():
    parser = build_parser()
    args = parser.parse_args()
    
    if args.watch:
        from organizer.watcher import watch_folder
        watch_folder(args.path)
        return

    run_organizer(
        folder_path=args.path,
        dry_run=args.dry_run,
        log_file=args.log_file
    )


if __name__ == "__main__":
    main()