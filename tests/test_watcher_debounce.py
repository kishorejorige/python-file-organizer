import time
from pathlib import Path

from organizer.watcher import Handler


class DummyEvent:
    def __init__(self, src_path, dest_path=None, is_directory=False):
        self.src_path = str(src_path)
        self.dest_path = str(dest_path) if dest_path else None
        self.is_directory = is_directory


class DummyEngine:
    def __init__(self):
        self.calls = []
        self.config = {"ignore_dirs": []}
        self.logger = None

    def process_file(self, root, path, dry_run=False):
        self.calls.append((root, Path(path), dry_run))


def test_debounce_on_created(tmp_path):
    engine = DummyEngine()
    handler = Handler(str(tmp_path), engine, dry_run=True, debounce_seconds=0.1)

    # simulate multiple quick create events for same file
    event = DummyEvent(tmp_path / "a.txt")
    handler.on_created(event)
    handler.on_created(event)
    handler.on_created(event)

    # wait for debounce to flush
    time.sleep(0.25)

    # should have processed only one batch
    assert len(engine.calls) == 1
