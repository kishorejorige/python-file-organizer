from pathlib import Path
from typing import List, Dict, Optional

from organizer.engine import rules as rules_module
from organizer.io import safe_move


class OrganizerEngine:
    def __init__(self, rules: List[Dict], config: Dict, logger):
        self.rules = rules
        self.config = config or {}
        self.logger = logger

    def should_skip(self, path: Path) -> bool:
        # skip non-files or symlinks for safety
        if not path.exists() or not path.is_file() or path.is_symlink():
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

    def process_file(
        self, root: Path, path: Path, dry_run: Optional[bool] = False
    ) -> Optional[Path]:
        if self.should_skip(path):
            if self.logger:
                self.logger.info(f"SKIPPED | {path}")
            return None

        category = rules_module.find_category_for_extension(self.rules, path.suffix)

        target_folder = root / category
        target_path = target_folder / path.name

        # Prevent path traversal: ensure target is strictly inside root
        try:
            resolved_root = root.resolve()
            resolved_target_folder = target_folder.resolve()
            if not str(resolved_target_folder).startswith(str(resolved_root)):
                if self.logger:
                    self.logger.error(
                        f"PATH TRAVERSAL PREVENTED | Root: {resolved_root}, Target: {resolved_target_folder}"
                    )
                return None
        except Exception as exc:
            if self.logger:
                self.logger.error(f"PATH TRAVERSAL EXCEPTION | {exc}")
            return None

        # avoid infinite loop: if target equals path, skip
        if path.resolve() == target_path.resolve():
            if self.logger:
                self.logger.warning(f"SKIPPED (same path) | {path}")
            return None

        # skip files already inside their target category folder
        if path.parent.resolve() == target_folder.resolve():
            if self.logger:
                self.logger.info(f"ALREADY ORGANIZED | {path}")
            return None

        if dry_run:
            if self.logger:
                self.logger.info(f"DRY RUN | {path} -> {target_path}")
            return target_path

        # perform safe move via IO layer
        try:
            target_folder.mkdir(parents=True, exist_ok=True)
            final, moved = safe_move(path, target_path)
            if self.logger:
                self.logger.info(f"MOVED | {path} -> {final}")
            return final
        except Exception as exc:  # pragma: no cover
            if self.logger:
                self.logger.exception(f"ERROR moving {path} -> {target_path}: {exc}")
            return None

    def _get_unique_filename(self, target_path: Path) -> Path:
        # Keep for backward compatibility if used elsewhere
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

        # Convert to static list to prevent directory modification during iteration
        if self.config.get("recursive", True):
            items = list(root.rglob("*"))
        else:
            items = list(root.iterdir())

        processed = 0
        for item in items:
            try:
                # Basic quick check before process_file
                if not item.is_file() or item.is_symlink():
                    continue

                res = self.process_file(root, item, dry_run=dry_run)
                if res:
                    processed += 1
            except Exception as exc:
                if self.logger:
                    self.logger.error(f"ERROR processing file '{item}': {exc}")

        if self.logger:
            self.logger.info(f"RUN COMPLETE | Processed Files: {processed}")
        return processed
