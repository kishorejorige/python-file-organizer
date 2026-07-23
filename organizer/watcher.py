import time
import threading
from pathlib import Path
from typing import Set, Optional

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ModuleNotFoundError:  # pragma: no cover
    Observer = None

    class FileSystemEventHandler:
        pass


from organizer.engine.organizer import OrganizerEngine


class Handler(FileSystemEventHandler):
    def __init__(
        self,
        path: str,
        engine: OrganizerEngine,
        dry_run: bool = False,
        debounce_seconds: float = 0.5,
    ):
        self.path = Path(path)
        self.engine = engine
        self.dry_run = dry_run
        self.debounce_seconds = debounce_seconds
        self._lock = threading.Lock()
        self._pending: Set[Path] = set()
        self._timer: Optional[threading.Timer] = None

    def on_created(self, event):
        if event.is_directory:
            return

        src = Path(event.src_path)

        # respect ignore dirs
        ignore = set(self.engine.config.get("ignore_dirs", []))
        if any(part in ignore for part in src.parts):
            return

        with self._lock:
            self._pending.add(src)
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._flush)
            self._timer.start()

    def on_moved(self, event):
        if event.is_directory:
            return
        try:
            dest = Path(event.dest_path)
        except Exception:
            dest = Path(event.src_path)

        with self._lock:
            self._pending.add(dest)
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._flush)
            self._timer.start()

    def on_modified(self, event):
        if event.is_directory:
            return
        src = Path(event.src_path)
        with self._lock:
            self._pending.add(src)
            if self._timer:
                self._timer.cancel()
            self._timer = threading.Timer(self.debounce_seconds, self._flush)
            self._timer.start()

    def _flush(self):
        with self._lock:
            items = list(self._pending)
            self._pending.clear()
            self._timer = None

        for src in items:
            try:
                self.engine.process_file(self.path, src, dry_run=self.dry_run)
            except Exception as exc:
                if self.engine.logger:
                    self.engine.logger.exception(
                        f"Error processing watched file {src}: {exc}"
                    )

    def stop(self):
        """Cancel any pending debounce timers."""
        with self._lock:
            if self._timer:
                self._timer.cancel()
                self._timer = None


def watch_folder(
    path: str,
    engine: OrganizerEngine,
    dry_run: bool = False,
    debounce_seconds: float = 0.5,
):
    if Observer is None:
        raise RuntimeError(
            "Watch mode requires the 'watchdog' package. Install project dependencies and try again."
        )

    p = Path(path)
    event_handler = Handler(
        str(p), engine, dry_run=dry_run, debounce_seconds=debounce_seconds
    )
    observer = Observer()
    observer.schedule(event_handler, str(p), recursive=True)

    observer.start()

    if engine.logger:
        engine.logger.info(f"Watching folder: {p}")
    else:
        print(f"Watching: {p}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        if engine.logger:
            engine.logger.info("Watcher stopped by user keyboard interrupt.")
    finally:
        observer.stop()
        event_handler.stop()
        observer.join()
