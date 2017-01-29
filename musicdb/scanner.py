import os
from .entry import MusicEntry

class MusicScanner:
    def __init__(self):
        self.accepted_extensions = ['.mp3']
        self.entries = []

    def scan_folder(self, folder_path):
        files = os.listdir(folder_path)

        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isdir(file_path):
                self.scan_folder(file_path)
                continue

            valid = False

            for ext in self.accepted_extensions:
                if file_path.endswith(ext):
                    valid = True
                    break

            if valid:
                self.entries.append(MusicEntry(file_path, file))
