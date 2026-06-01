from pathlib import Path
from typing import Tuple
import shutil


def safe_move(src: Path, dest: Path) -> Tuple[Path, bool]:
    """Move src to dest safely.

    Returns (final_dest, moved_flag). If dest exists, creates unique name.
    """
    dest_parent = dest.parent
    dest_parent.mkdir(parents=True, exist_ok=True)

    final = dest
    counter = 1
    stem = dest.stem
    suffix = dest.suffix
    while final.exists():
        final = dest_parent / f"{stem}_{counter}{suffix}"
        counter += 1

    shutil.move(str(src), str(final))
    return final, True
