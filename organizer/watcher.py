import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from organizer.main import run_organizer


class Handler(FileSystemEventHandler):

    def __init__(self, path):
        self.path = path

    def on_created(self, event):
        if not event.is_directory:
            run_organizer(self.path, dry_run=False)


def watch_folder(path):
    event_handler = Handler(path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    observer.start()

    print(f"Watching: {path}")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
