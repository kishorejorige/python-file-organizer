from config import FILE_TYPES

def get_category(extension):
    extension = extension.lower()


    for category, extensions in FILE_TYPES.items():
        if extension in extensions:
            return category

    return "Others"

