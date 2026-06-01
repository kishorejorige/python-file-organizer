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


def is_hidden(path):
    return any(part.startswith('.') for part in path.parts)

