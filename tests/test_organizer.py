import pytest
from organizer.engine.organizer import OrganizerEngine
from organizer.logger import setup_logger


def test_import_main():
    from organizer.main import main

    assert callable(main)


def test_skips_symlinks(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    # Create a regular file
    reg_file = root / "real_doc.txt"
    reg_file.write_text("content")

    # Create a symlink pointing to the regular file
    sym_file = root / "link_doc.txt"
    try:
        sym_file.symlink_to(reg_file)
    except OSError:
        # Windows developer mode might be off, skip symlink creation and assert nothing
        pytest.skip("Symlink creation not supported in this environment")

    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(None)
    cfg = {"ignore_dirs": [], "recursive": False}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    # Process files
    processed = engine.run(root, dry_run=False)

    # The real file should be processed (moved to Documents/real_doc.txt), but the symlink skipped
    assert processed == 1
    assert not reg_file.exists()
    assert (root / "Documents" / "real_doc.txt").exists()
    assert sym_file.is_symlink()  # Symlink itself should not be moved/deleted


def test_path_traversal_prevention(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    file_path = root / "file.txt"
    file_path.write_text("hello")

    # Malformed category rule that tries to escape the root
    rules = [{"folder": "../escaped_dir", "extensions": [".txt"]}]
    logger = setup_logger(None)
    cfg = {"ignore_dirs": [], "recursive": False}

    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    # Let's call process_file directly or via run. Since "folder" contains "..",
    # the target path would be root / "../escaped_dir" which is outside the root.
    # validate_rules would normally catch this at startup, but process_file's internal containment
    # check acts as a secondary layer of protection.
    res = engine.process_file(root, file_path, dry_run=False)
    assert res is None
    assert file_path.exists()  # File should not be moved


def test_already_organized_skips(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    target_folder = root / "Documents"
    target_folder.mkdir()

    file_path = target_folder / "file.txt"
    file_path.write_text("hello")

    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(None)
    cfg = {"ignore_dirs": [], "recursive": False}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    res = engine.process_file(root, file_path, dry_run=False)
    assert res is None  # Should return None (skipped since it's already organized)
    assert file_path.exists()  # Stays where it is


def test_one_file_failure_isolation(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    f1 = root / "good1.txt"
    f1.write_text("a")

    # We will trigger a failure on process_file for f2 by using a mock or a file that is deleted in the middle
    f2 = root / "bad.txt"
    f2.write_text("b")

    f3 = root / "good2.txt"
    f3.write_text("c")

    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(None)
    cfg = {"ignore_dirs": [], "recursive": False}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    # Let's subclass or monkeypatch process_file to raise an Exception on bad.txt
    original_process = engine.process_file

    def mock_process_file(r, path, dry_run=False):
        if path.name == "bad.txt":
            raise PermissionError("Mock permission error")
        return original_process(r, path, dry_run=dry_run)

    engine.process_file = mock_process_file

    processed = engine.run(root, dry_run=False)

    # It should successfully process 2 files and skip the bad one without raising an exception to the caller
    assert processed == 2
    assert (root / "Documents" / "good1.txt").exists()
    assert (root / "Documents" / "good2.txt").exists()
    assert f2.exists()  # The bad one remains unmoved


def test_sibling_path_traversal_prevention(tmp_path):
    root = tmp_path / "root"
    root.mkdir()

    # Create sibling folder
    sibling = tmp_path / "root_sibling"
    sibling.mkdir()

    file_path = root / "file.txt"
    file_path.write_text("hello")

    # A rule trying to escape into a sibling folder
    rules = [{"folder": "../root_sibling", "extensions": [".txt"]}]
    logger = setup_logger(None)
    cfg = {"ignore_dirs": [], "recursive": False}

    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)
    res = engine.process_file(root, file_path, dry_run=False)
    assert res is None
    assert file_path.exists()
