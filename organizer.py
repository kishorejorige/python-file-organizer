from pathlib import Path
import shutil
import sys

from utils import get_category

if len(sys.argv) < 2:
    print("Usage: python organizer.py <folder_path>")
    sys.exit()
    
folder_path = Path(sys.argv[1])

if not folder_path.exists():
    print("Error: Folder does not exist")
    sys.exit()

if not folder_path.is_dir():
    print("Error: Provided path is not a folder")
    sys.exit()

for item in folder_path.iterdir():
    if item.is_file():
        extension = item.suffix


        category = get_category(extension)

        target_folder = folder_path / category

        target_folder.mkdir(exist_ok=True)

        target_path = target_folder / item.name

        shutil.move(str(item), str(target_path))

        print(f"Moved: {item.name} -> {category}")

