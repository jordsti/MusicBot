import MySQLdb
import time
from .entry import MusicEntry, MusicTag
from .migration import generate_structures_hash, DbStructureVersion
import sqlite3

class Database:
    def __init__(self):
        self.__init_tables()
        self.migrations = []

    def __init_tables(self):
        pass

    def __add_initial_db_version(self, conn):
        pass

    def connect(self):
        pass

    def remove_db_version(self, db_version):
        pass

    def add_db_version(self, db_version):
        pass

    def get_db_versions(self, conn=None):
        pass

    def add_music_entry(self, music_entry):
        pass

    def add_music_tag(self, music_entry):
        pass

    def get_music_entry_id_from_filepath(self, file_path):
        pass

    def get_entries_by_album(self, album, count=100):
        pass

    def get_entries_by_title(self, title, count=100):
        pass

    def add_keyword(self, music_entry_id, keyword):
        pass

class SQLiteIterator:
    def __init__(self, table_name, column_name, current=0, step=1):
        self.table_name = table_name
        self.column_name = column_name
        self.__current = current
        self.__step = step

    def current(self):
        return self.__current

    def next(self):
        self.__current += self.__step
        return self.__current

    def step(self):
        return self.__step

class SQLiteDatabase(Database):
    (MusicEntry, MusicTag, MusicKeyword) = ("music_entries", "music_tags", "music_keywords")

    def __init__(self, file='database.sqlite'):
        Database.__init__(self)
        self.conn = sqlite3.connect(file)
        self.file = file
        self.iterators = {}

        self.__init_tables()

    def __init_tables(self):
        cur = self.conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS `music_entries` (
                      `music_entry_id` int(11) NOT NULL,
                      `file_path` varchar(255) NOT NULL,
                      `file_name` varchar(255) NOT NULL,
                      `file_hash` varchar(32) NOT NULL,
                      `added_on` int(11) NOT NULL,
                      PRIMARY KEY (`music_entry_id`)
                    ); """)

        cur.execute("""CREATE TABLE IF NOT EXISTS `music_tags` (
                      `music_tag_id` int(11) NOT NULL,
                      `music_entry_id` int(11) NOT NULL,
                      `title` varchar(255) NOT NULL,
                      `album` varchar(255) NOT NULL,
                      `artist` varchar(255) NOT NULL,
                      `track` int(11) NULL,
                      `tag_hash` varchar(32) NOT NULL,
                      `added_on` int(11) NOT NULL,
                      PRIMARY KEY (`music_tag_id`)
                    ); """)

        cur.execute("""CREATE TABLE IF NOT EXISTS `music_keywords` (
                              `music_keyword_id` int(11) NOT NULL,
                              `music_entry_id` int(11) NOT NULL,
                              `keywords` TEXT NOT NULL,
                              PRIMARY KEY (`music_keyword_id`)
                            ); """)

        self.conn.commit()

        # music_entries iterator
        rs = cur.execute("""SELECT music_entry_id FROM music_entries ORDER BY music_entry_id DESC LIMIT 1""")
        row = cur.fetchone()
        if row:
            self.iterators[self.MusicEntry] = SQLiteIterator("music_entries", "music_entry_id", int(row[0]))
        else:
            self.iterators[self.MusicEntry] = SQLiteIterator("music_entries", "music_entry_id")

        # music tags
        rs = cur.execute("""SELECT music_tag_id FROM music_tags ORDER BY music_entry_id DESC LIMIT 1""")
        row = cur.fetchone()
        if row:
            self.iterators[self.MusicTag] = SQLiteIterator("music_tags", "music_tag_id", int(row[0]))
        else:
            self.iterators[self.MusicTag] = SQLiteIterator("music_tags", "music_tag_id")

        # music keywords
        rs = cur.execute("""SELECT music_keyword_id FROM music_keywords ORDER BY music_entry_id DESC LIMIT 1""")
        row = cur.fetchone()
        if row:
            self.iterators[self.MusicKeyword] = SQLiteIterator("music_keywords", "music_keyword_id", int(row[0]))
        else:
            self.iterators[self.MusicKeyword] = SQLiteIterator("music_keywords", "music_keyword_id")

        cur.close()

    def __add_initial_db_version(self, conn):
        pass

    def connect(self):
        pass

    def remove_db_version(self, db_version):
        pass

    def add_db_version(self, db_version):
        pass

    def get_db_versions(self, conn=None):
        pass

    def add_music_entry(self, music_entry):
        cur = self.conn.cursor()
        timestamp = int(time.time())
        music_entry_id = self.iterators[self.MusicEntry].next()
        query = """INSERT INTO music_entries (music_entry_id, file_path, file_name, file_hash, added_on) VALUES (?, ?, ?, ?, ?)"""
        cur.execute(query, (music_entry_id, music_entry.file_path, music_entry.filename, music_entry.hash, timestamp, ))
        self.conn.commit()
        cur.close()

        music_entry.id = music_entry_id
        music_entry.timestamp = timestamp

    def add_music_tag(self, music_entry):
        cur = self.conn.cursor()
        timestamp = int(time.time())
        music_entry.tag.id = self.iterators[self.MusicTag].next()
        query = """INSERT INTO music_tags (music_tag_id, music_entry_id, title, album, artist, track, tag_hash, added_on) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        cur.execute(query, (music_entry.tag.id, music_entry.id, music_entry.tag.title, music_entry.tag.album, music_entry.tag.artist, music_entry.tag.track, music_entry.tag.hash, timestamp, ))
        self.conn.commit()
        cur.close()

    def get_music_entry_id_from_filepath(self, file_path):
        music_entry_id = 0
        cur = self.conn.cursor()

        query = """SELECT music_entry_id FROM music_entries WHERE file_path = ?"""

        cur.execute(query, (file_path,))

        row = cur.fetchone()
        if row:
            music_entry_id = int(row[0])

        cur.close()
        return music_entry_id

    def get_entries_by_album(self, album, count=100):
        entries = []
        cur = self.conn.cursor()

        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.track, t.tag_hash
                FROM music_tags t
                JOIN music_entries e ON e.music_entry_id = t.music_entry_id
                WHERE t.album LIKE ?
                ORDER BY t.track
                LIMIT ?;"""

        cur.execute(query, ("%{0}%".format(album), count, ))

        rows = cur.fetchall()

        for row in rows:
            music_entry = MusicEntry(row[1], row[2])
            music_entry.id = int(row[0])
            music_entry.hash = row[3]
            music_entry.added_on = int(row[4])

            music_entry.tag = MusicTag()
            music_entry.tag.id = int(row[5])
            music_entry.tag.title = row[6]
            music_entry.tag.artist = row[7]
            music_entry.tag.album = row[8]
            music_entry.tag.track = int(row[9])
            music_entry.tag.hash = row[10]

            entries.append(music_entry)

        cur.close()

        return entries

    def get_entries_by_title(self, title, count=100):
        entries = []
        cur = self.conn.cursor()

        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.track, t.tag_hash
                FROM music_tags t
                JOIN music_entries e ON e.music_entry_id = t.music_entry_id
                JOIN music_keywords k ON k.music_entry_id = t.music_entry_id
                WHERE t.title LIKE ? OR k.keywords LIKE ?
                LIMIT ? """

        cur.execute(query, ("%{0}%".format(title), "%{0}%".format(title), count, ))

        rows = cur.fetchall()

        for row in rows:
            music_entry = MusicEntry(row[1], row[2])
            music_entry.id = int(row[0])
            music_entry.hash = row[3]
            music_entry.added_on = int(row[4])

            music_entry.tag = MusicTag()
            music_entry.tag.id = int(row[5])
            music_entry.tag.title = row[6]
            music_entry.tag.artist = row[7]
            music_entry.tag.album = row[8]
            music_entry.tag.track = int(row[9])
            music_entry.tag.hash = row[10]

            entries.append(music_entry)

        cur.close()
        return entries

    def add_keyword(self, music_entry_id, keyword):
        cur = self.conn.cursor()
        id = self.iterators[self.MusicKeyword].next()
        query = """INSERT INTO music_keywords (music_keyword_id, music_entry_id, keywords) VALUES (?, ?, ?)"""
        cur.execute(query, (id, music_entry_id, keyword, ))
        self.conn.commit()
        cur.close()

