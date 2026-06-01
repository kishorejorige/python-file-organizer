import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from organizer.engine.organizer import OrganizerEngine


class Handler(FileSystemEventHandler):

    def __init__(self, path: str, engine: OrganizerEngine, dry_run: bool = False):
        self.path = Path(path)
        self.engine = engine
        self.dry_run = dry_run

    def on_created(self, event):
        if not event.is_directory:
            # process single created file
            src = Path(event.src_path)
            try:
                self.engine.process_file(self.path, src, dry_run=self.dry_run)
            except Exception:
                pass


def watch_folder(path: str, engine: OrganizerEngine, dry_run: bool = False):
    p = Path(path)
    event_handler = Handler(str(p), engine, dry_run=dry_run)
    observer = Observer()
    observer.schedule(event_handler, str(p), recursive=True)

    observer.start()

    print(f"Watching: {p}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
