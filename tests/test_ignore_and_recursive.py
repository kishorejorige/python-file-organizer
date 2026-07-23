from organizer.engine.organizer import OrganizerEngine
from organizer.logger import setup_logger


def test_ignore_dirs_respected(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    ignored = root / ".git"
    ignored.mkdir()
    f = ignored / "secret.txt"
    f.write_text("x")

    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(str(tmp_path / "log.log"))
    cfg = {"ignore_dirs": [".git"], "recursive": True}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    processed = engine.run(root, dry_run=False)
    # should not process hidden file
    assert processed == 0


def test_non_recursive_scan(tmp_path):
    root = tmp_path / "root2"
    root.mkdir()
    sub = root / "sub"
    sub.mkdir()
    f = sub / "a.txt"
    f.write_text("x")

    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(str(tmp_path / "log.log"))
    cfg = {"ignore_dirs": [], "recursive": False}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    processed = engine.run(root, dry_run=False)
    assert processed == 0
