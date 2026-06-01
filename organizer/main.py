from pathlib import Path
import shutil

from organizer.utils import get_category, get_unique_filename
from organizer.logger import log_info


def run_organizer(folder_path, dry_run=False, log_file="logs/organizer.log"):

    folder_path = Path(folder_path)

    if not folder_path.exists():
        print("Error: Folder does not exist")
        return

    if not folder_path.is_dir():
        print("Error: Provided path is not a folder")
        return

    processed = 0

    for item in folder_path.rglob("*"):

        if not item.is_file():
            continue

        # skip already organized folders
        if any(part in ["Images", "Documents", "Videos", "Audio", "Archives", "Code", "Executables", "Libraries", "Others"]
               for part in item.parts):
            continue

        extension = item.suffix.lower()
        category = get_category(extension)

        target_folder = folder_path / category
        target_folder.mkdir(exist_ok=True)

        target_path = target_folder / item.name
        target_path = get_unique_filename(target_path)

        if dry_run:
            print(f"Would move: {item.name} -> {target_path}")
            log_info(log_file, f"DRY RUN | {item.name} -> {target_path}")
        else:
            shutil.move(str(item), str(target_path))
            print(f"Moved: {item.name} -> {target_path}")
            log_info(log_file, f"MOVED | {item.name} -> {target_path}")

        processed += 1

    print("\nOrganization Complete")
    print(f"Total processed files: {processed}")

    log_info(log_file, f"RUN COMPLETE | Processed Files: {processed}")