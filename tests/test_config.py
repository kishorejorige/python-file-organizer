from organizer.config import FILE_TYPES


def test_file_types_exist():
    assert "Images" in FILE_TYPES
    assert "Documents" in FILE_TYPES
    assert "Audio" in FILE_TYPES