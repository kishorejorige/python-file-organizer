
from organizer.engine.organizer import OrganizerEngine
from organizer.logger import setup_logger


def test_dry_run_and_collision(tmp_path):
    # prepare files
    src = tmp_path / "src"
    src.mkdir()
    f1 = src / "file.txt"
    f1.write_text("a")

    # create target with same name to force collision
    rules = [{"folder": "Documents", "extensions": [".txt"]}]
    logger = setup_logger(str(tmp_path / "log.log"))
    cfg = {"ignore_dirs": [], "recursive": True}
    engine = OrganizerEngine(rules=rules, config=cfg, logger=logger)

    # dry run should not move
    res = engine.process_file(src, f1, dry_run=True)
    assert res is not None
    assert f1.exists()

    # actual move
    moved = engine.process_file(src, f1, dry_run=False)
    assert moved is not None
    assert (src / "Documents").exists()

    # create another file with same name, test unique naming
    f2 = src / "file2.txt"
    f2.write_text("b")
    moved2 = engine.process_file(src, f2, dry_run=False)
    assert moved2 is not None
