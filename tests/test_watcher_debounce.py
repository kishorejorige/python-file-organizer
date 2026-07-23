import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from organizer.watcher import Handler, watch_folder


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
    time.sleep(0.2)

    # should have processed only one batch
    assert len(engine.calls) == 1
    handler.stop()


def test_directory_event_ignored(tmp_path):
    engine = DummyEngine()
    handler = Handler(str(tmp_path), engine, dry_run=True, debounce_seconds=0.01)

    event = DummyEvent(tmp_path / "subdir", is_directory=True)
    handler.on_created(event)

    time.sleep(0.03)
    assert len(engine.calls) == 0
    handler.stop()


def test_on_moved_event(tmp_path):
    engine = DummyEngine()
    handler = Handler(str(tmp_path), engine, dry_run=True, debounce_seconds=0.05)

    event = DummyEvent(tmp_path / "old.txt", dest_path=tmp_path / "new.txt")
    handler.on_moved(event)

    time.sleep(0.1)
    assert len(engine.calls) == 1
    assert engine.calls[0][1].name == "new.txt"
    handler.stop()


def test_organizer_failure_logging(tmp_path):
    class ExceptionEngine:
        def __init__(self):
            self.config = {"ignore_dirs": []}
            self.logger = MagicMock()

        def process_file(self, root, path, dry_run=False):
            raise RuntimeError("Mock error processing file")

    engine = ExceptionEngine()
    handler = Handler(str(tmp_path), engine, dry_run=True, debounce_seconds=0.01)

    event = DummyEvent(tmp_path / "fail.txt")
    handler.on_created(event)

    time.sleep(0.03)
    engine.logger.exception.assert_called_once()
    handler.stop()


def test_watch_folder_lifecycle():
    mock_engine = MagicMock()
    mock_observer = MagicMock()

    with patch(
        "organizer.watcher.Observer", return_value=mock_observer
    ) as mock_obs_class:
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            watch_folder("/mock/path", mock_engine, dry_run=True, debounce_seconds=0.01)

            mock_obs_class.assert_called_once()
            mock_observer.schedule.assert_called_once()
            mock_observer.start.assert_called_once()
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()
