from pathlib import Path
import shutil
from typing import List, Dict, Optional

from organizer.engine import rules as rules_module


class OrganizerEngine:
    def __init__(self, rules: List[Dict], config: Dict, logger):
        self.rules = rules
        self.config = config or {}
        self.logger = logger

    def should_skip(self, path: Path) -> bool:
        # skip non-files
        if not path.exists() or not path.is_file():
            return True

        # skip hidden files or files in hidden dirs
        if any(part.startswith(".") for part in path.parts):
            return True

        # skip files already in target rule folders
        rule_folders = {r.get("folder") for r in self.rules}
        if any(part in rule_folders for part in path.parts):
            return True

        # ignore configured dirs
        ignore = set(self.config.get("ignore_dirs", []))
        if any(part in ignore for part in path.parts):
            return True

        return False

    def process_file(self, root: Path, path: Path, dry_run: Optional[bool] = False) -> Optional[Path]:
        if self.should_skip(path):
            if self.logger:
                self.logger.info(f"SKIPPED | {path}")
            return None

        category = rules_module.find_category_for_extension(self.rules, path.suffix)

        target_folder = root / category
        target_folder.mkdir(parents=True, exist_ok=True)

        target_path = target_folder / path.name

        # avoid infinite loop: if target is inside source tree and equals path, skip
        try:
            target_path = self._get_unique_filename(target_path)
        except Exception:
            if self.logger:
                self.logger.warning(f"Could not compute unique filename for {target_path}")
            return None

        if dry_run:
            if self.logger:
                self.logger.info(f"DRY RUN | {path} -> {target_path}")
            return target_path

        # perform move
        shutil.move(str(path), str(target_path))
        if self.logger:
            self.logger.info(f"MOVED | {path} -> {target_path}")
        return target_path

    def _get_unique_filename(self, target_path: Path) -> Path:
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

    def run(self, root_path: Path, dry_run: Optional[bool] = False):
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Root path not found: {root}")

        processed = 0
        # rglob with pattern to find files
        if self.config.get("recursive", True):
            iterator = root.rglob("*")
        else:
            iterator = root.iterdir()

        for item in iterator:
            if not item.is_file():
                continue

            res = self.process_file(root, item, dry_run=dry_run)
            if res:
                processed += 1

        if self.logger:
            self.logger.info(f"RUN COMPLETE | Processed Files: {processed}")
        return processed
