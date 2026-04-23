import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class SimpleHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print(f"Event: {event.event_type} at {event.src_path}")

if __name__ == "__main__":
    path = os.path.abspath("./raw")
    print(f"Testing watchdog on: {path}")
    event_handler = SimpleHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
