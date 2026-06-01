import argparse
import shutil
from pathlib import Path

from organizer.config import FILE_TYPES
from organizer.logger import setup_logger
from organizer.utils import get_category, get_unique_filename

ORGANIZED_FOLDERS = set(FILE_TYPES.keys())

logger = setup_logger()


def organize_folder(folder_path: Path, dry_run: bool = False) -> int:
    moved_files = 0

    for item in folder_path.rglob("*"):

        if any(part in ORGANIZED_FOLDERS for part in item.parts):
            continue

        if item.is_file():

            category = get_category(item.suffix)

            target_folder = folder_path / category
            target_folder.mkdir(exist_ok=True)

            target_path = target_folder / item.name
            target_path = get_unique_filename(target_path)

            if dry_run:
                print(f"Would move: {item.name} -> {target_path}")
                logger.info(
                    f"DRY RUN | {item.name} -> {target_path}"
                )

            else:
                shutil.move(str(item), str(target_path))

                print(f"Moved: {item.name} -> {target_path}")

                logger.info(
                    f"MOVED | {item.name} -> {target_path}"
                )
                
            moved_files += 1

    print("\nOrganization Complete")
    print(f"Total processed files: {moved_files}")
    
    return moved_files


def main():
    parser = argparse.ArgumentParser(
        description="Automatically organize files by type."
    )

    parser.add_argument(
        "folder",
        help="Folder to organize"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without moving files"
    )

    args = parser.parse_args()

    folder_path = Path(args.folder)

    if not folder_path.exists():
        logger.error(
            f"Folder does not exist: {folder_path}"
        )
        print("Error: Folder does not exist")
        return

    if not folder_path.is_dir():
        logger.error(
            f"Path is not a directory: {folder_path}"
        )

        print("Error: Provided path is not a folder")
        return
    
    moved_files = organize_folder(
        folder_path,
        dry_run=args.dry_run
    )

    logger.info(
        f"RUN COMPLETE | Processed Files: {moved_files}"
    )
    
    organize_folder(folder_path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
