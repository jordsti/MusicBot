from .database import Database, SQLiteDatabase
from .MySqlDatabase import MySqlDatabase
from .scanner import MusicScanner
from .migration import MigrationManager

class MusicDb:
    def __init__(self, root, db_driver, db_info):
        self.migration_manager = None
        if db_driver == 'sqlite':
            self.database = SQLiteDatabase(db_info['filename'])
        elif db_driver == 'mysql':
            self.database = MySqlDatabase(db_info['user'], db_info['password'], db_info['name'], db_info['address'])
            self.migration_manager = MigrationManager(self.database)

        self.scanner = MusicScanner()
        self.root = root

    def update_database_schema(self):
        if self.migration_manager is not None:
            self.migration_manager.run_migrations()

    def scan(self, verbose=True):
        self.scanner.scan_folder(self.root)
        nb_entries = len(self.scanner.entries)
        i = 0

        for entry in self.scanner.entries:
            progress = (i / nb_entries) * 100
            music_entry_id = self.database.get_music_entry_id_from_filepath(entry.file_path)

            if music_entry_id == 0:
                if verbose:
                    print("Importing new music file : {0}".format(entry.file_path))
                # file hashing
                entry.hash_file()
                self.database.add_music_entry(entry)
                # reading id3 tags
                try:
                    entry.read_tags()
                    self.database.add_music_tag(entry)
                    keyword = "{0} {1} {2}".format(entry.tag.artist, entry.tag.title, entry.tag.album)
                    self.database.add_keyword(entry.id, keyword)
                except:
                    print("ID3 error")
            if verbose:
                print("Scanning progress {0:.2f}% ({1}/{2})".format(progress, i, nb_entries))

            i += 1
        if verbose:
            print("Scanning complete")

    def search(self, title, count=100):
        return self.database.get_entries_by_title(title, count)

    def search_album(self, album):
        return self.database.get_entries_by_album(album)

