from config import FILE_TYPES
from pathlib import Path

def get_category(extension):
    extension = extension.lower()


    for category, extensions in FILE_TYPES.items():
        if extension in extensions:
            return category

    return "Others"

def get_unique_filename(target_path):
    counter = 1
    
    file_stem = target_path.stem
    file_suffix = target_path.suffix
    
    parent_dir = target_path.parent
    
    new_path = target_path
    
    while new_path.exists():
        new_filename = f"{file_stem}_{counter}{file_suffix}"
        new_path = parent_dir / new_filename
        
        counter += 1
        
    return new_path

