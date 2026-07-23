from pathlib import Path

from organizer.utils import get_unique_filename


def test_unique_filename():
    path = Path("photo.jpg")

    result = get_unique_filename(path)

    assert result is not None
