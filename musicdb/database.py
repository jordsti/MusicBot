import MySQLdb
import time
from .entry import MusicEntry, MusicTag

class Database:
    def __init__(self,db_user, db_password, db_database, hostname='localhost', port=3306, charset='utf8'):
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database
        self.hostname = hostname
        self.port = port
        self.charset = charset
        self.__init_tables()

    def __init_tables(self):
        conn = self.connect()
        cur = conn.cursor()

        cur.execute("""CREATE TABLE IF NOT EXISTS `music_entries` (
                      `music_entry_id` int(11) NOT NULL AUTO_INCREMENT,
                      `file_path` varchar(255) NOT NULL,
                      `file_name` varchar(255) NOT NULL,
                      `file_hash` varchar(32) NOT NULL,
                      `added_on` int(11) NOT NULL,
                      PRIMARY KEY (`music_entry_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """)

        cur.execute("""CREATE TABLE IF NOT EXISTS `music_tags` (
                      `music_tag_id` int(11) NOT NULL AUTO_INCREMENT,
                      `music_entry_id` int(11) NOT NULL,
                      `title` varchar(255) NOT NULL,
                      `album` varchar(255) NOT NULL,
                      `artist` varchar(255) NOT NULL,
<<<<<<< HEAD
                      `track` int(11) NULL,
=======
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778
                      `tag_hash` varchar(32) NOT NULL,
                      `added_on` int(11) NOT NULL,
                      PRIMARY KEY (`music_tag_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """)

        conn.commit()
        cur.close()
        conn.close()

    def connect(self):
        conn = None
        try:
            conn = MySQLdb.Connect(host=self.hostname, port=self.port, user=self.db_user, password=self.db_password, db=self.db_database, charset=self.charset)
        except Exception as e:
            print("MySQL Connection error : {0}".format(e))
        return conn

    def add_music_entry(self, music_entry):
        conn = self.connect()
        cur = conn.cursor()
        timestamp = int(time.time())

        query = """INSERT INTO music_entries (file_path, file_name, file_hash, added_on) VALUES (%s, %s, %s, %s)"""

        cur.execute(query, (music_entry.file_path, music_entry.filename, music_entry.hash, timestamp, ))

        conn.commit()

        # selecting id
        query = """SELECT music_entry_id FROM music_entries WHERE file_path = %s AND file_hash = %s AND added_on = %s"""

        cur.execute(query, (music_entry.file_path, music_entry.hash, timestamp, ))

        row = cur.fetchone()

        if row:
            music_entry.id = int(row[0])
            music_entry.added_on = timestamp

        cur.close()
        conn.close()

    def add_music_tag(self, music_entry):
        conn = self.connect()
        cur = conn.cursor()
        timestamp = int(time.time())

<<<<<<< HEAD
        query = """INSERT INTO music_tags (music_entry_id, title, album, artist, track, tag_hash, added_on) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cur.execute(query, (music_entry.id, music_entry.tag.title, music_entry.tag.album, music_entry.tag.artist, music_entry.tag.track, music_entry.tag.hash, timestamp, ))
=======
        query = """INSERT INTO music_tags (music_entry_id, title, album, artist, tag_hash, added_on) VALUES (%s, %s, %s, %s, %s, %s)"""

        cur.execute(query, (music_entry.id, music_entry.tag.title, music_entry.tag.album, music_entry.tag.artist, music_entry.tag.hash, timestamp, ))
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778

        conn.commit()

        query = """SELECT music_tag_id FROM music_tags WHERE music_entry_id = %s AND tag_hash = %s"""
        cur.execute(query, (music_entry.id, music_entry.tag.hash, ))

        row = cur.fetchone()

        if row:
            music_entry.tag.id = int(row[0])

        cur.close()
        conn.close()

    def get_music_entry_id_from_filepath(self, file_path):
        music_entry_id = 0
        conn = self.connect()
        cur = conn.cursor()

        query = """SELECT music_entry_id FROM music_entries WHERE file_path = %s"""

        cur.execute(query, (file_path,))

        row = cur.fetchone()
        if row:
            music_entry_id = int(row[0])

        cur.close()
        conn.close()

        return music_entry_id

<<<<<<< HEAD
    def get_entries_by_album(self, album, count=100):
        entries = []

        conn = self.connect()
        cur = conn.cursor()

        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.track, t.tag_hash
                FROM music_tags t
                JOIN music_entries e ON e.music_entry_id = t.music_entry_id
                WHERE t.album LIKE %s
                ORDER BY t.track
                LIMIT %s;"""

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
        conn.close()

        return entries

=======
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778
    def get_entries_by_title(self, title, count=100):
        entries = []

        conn = self.connect()
        cur = conn.cursor()

<<<<<<< HEAD
        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.track, t.tag_hash
=======
        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.tag_hash
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778
                FROM music_tags t
                JOIN music_entries e ON e.music_entry_id = t.music_entry_id
                WHERE t.title LIKE %s
                LIMIT %s """

        cur.execute(query, ("%{0}%".format(title), count, ))

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
<<<<<<< HEAD
            music_entry.tag.track = int(row[9])
            music_entry.tag.hash = row[10]
=======
            music_entry.tag.hash = row[9]
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778

            entries.append(music_entry)

        cur.close()
        conn.close()

        return entries
