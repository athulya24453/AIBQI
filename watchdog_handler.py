import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class Watcher:
    DIRECTORY_TO_WATCH = "input"  # The folder to monitor

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None

        elif event.src_path.endswith((".png", ".jpg", ".jpeg")):
            print(f"New image detected: {event.src_path}")
            # Run your Python script here
            subprocess.run(["python", "your_script.py"])

if __name__ == "__main__":
    w = Watcher()
    w.run()