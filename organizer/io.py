from pathlib import Path
from typing import Tuple
import os
import shutil


def safe_move(src: Path, dest: Path) -> Tuple[Path, bool]:
    """Move src to dest safely.

    Returns (final_dest, moved_flag). If dest exists, creates unique name.

    Implementation notes:
    - Attempts an atomic rename into the destination directory when possible.
    - Falls back to ``shutil.move`` for cross-filesystem moves.
    - Avoids overwriting by creating a unique filename.
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

    # Try atomic move via os.replace using a temporary name in target dir.
    # This is atomic on the same filesystem. If it fails (different FS), fall back.
    try:
        tmp_name = dest_parent / f".{stem}.tmp{os.getpid()}"
        try:
            # Attempt fast atomic move (rename)
            os.replace(str(src), str(tmp_name))
            os.replace(str(tmp_name), str(final))
        except OSError:
            # Could not rename across filesystems; fall back to shutil.move
            if tmp_name.exists():
                try:
                    tmp_name.unlink()
                except Exception:  # nosec B110
                    pass
            shutil.move(str(src), str(final))

        return final, True
    except Exception:
        # Last-resort attempt
        shutil.move(str(src), str(final))
        return final, True
