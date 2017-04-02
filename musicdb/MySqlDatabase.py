from .database import Database

class MySqlDatabase(Database):
    def __init__(self, db_user, db_password, db_database, hostname='localhost', port=3306, charset='utf8'):
        Database.__init__(self)
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database
        self.hostname = hostname
        self.port = port
        self.charset = charset
        self.__init_tables()
        self.migrations = []

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
                      `track` int(11) NULL,
                      `tag_hash` varchar(32) NOT NULL,
                      `added_on` int(11) NOT NULL,
                      PRIMARY KEY (`music_tag_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """)

        cur.execute("""CREATE TABLE IF NOT EXISTS `musicdb_versions` (
                        `musicdb_version_id` INT(11) NOT NULL AUTO_INCREMENT,
                        `migration_name` VARCHAR(255) NOT NULL,
                        `structure_hash` VARCHAR(64) NOT NULL,
                        `executed_on` INT(11) NOT NULL,
                        `version_number` INT(11) NOT NULL,
                        PRIMARY KEY (`musicdb_version_id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """)

        query = """SELECT COUNT(musicdb_version_id) FROM musicdb_versions"""
        cur.execute(query)

        conn.commit()

        row = cur.fetchone()
        if row:
            if row[0] == 0:
                self.__add_initial_db_version(conn)

        conn.commit()
        cur.close()
        conn.close()

    def __add_initial_db_version(self, conn):
        # generating structure hash
        database_hash = generate_structures_hash(conn)
        db_version = DbStructureVersion("Initial Structure", database_hash, int(time.time()), 0)
        self.add_db_version(db_version)

    def connect(self):
        conn = None
        try:
            conn = MySQLdb.Connect(host=self.hostname, port=self.port, user=self.db_user, password=self.db_password, db=self.db_database, charset=self.charset)
        except Exception as e:
            print("MySQL Connection error : {0}".format(e))
        return conn

    def remove_db_version(self, db_version):
        conn = self.connect()
        cur = conn.cursor()

        query = """DELETE FROM musicdb_versions WHERE musicdb_version_id = %s"""
        cur.execute(query, (db_version.id,))

        conn.commit()
        cur.close()
        conn.close()

    def add_db_version(self, db_version):
        conn = self.connect()
        cur = conn.cursor()

        query = """INSERT INTO musicdb_versions (migration_name, structure_hash, executed_on, version_number) VALUES (%s, %s, %s, %s)"""
        cur.execute(query, (db_version.migration_name, db_version.structure_hash, db_version.executed_on, db_version.version_number, ))

        conn.commit()

        query = """SELECT musicdb_version_id FROM musicdb_versions WHERE structure_hash = %s AND version_number = %s"""
        cur.execute(query, (db_version.structure_hash, db_version.version_number,))

        row = cur.fetchone()
        if row:
            db_version.id = int(row[0])

        cur.close()
        conn.close()

    def get_db_versions(self, conn=None):
        versions = []
        if conn is None:
            conn = self.connect()

        cur = conn.cursor()

        query = """SELECT musicdb_version_id, migration_name, structure_hash, executed_on, version_number FROM musicdb_versions"""

        cur.execute(query)

        rows = cur.fetchall()

        for row in rows:
            db_version = DbStructureVersion(row[1], row[2], int(row[3]), row[4], row[0])
            versions.append(db_version)

        cur.close()
        conn.close()

        return versions

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

        query = """INSERT INTO music_tags (music_entry_id, title, album, artist, track, tag_hash, added_on) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cur.execute(query, (music_entry.id, music_entry.tag.title, music_entry.tag.album, music_entry.tag.artist, music_entry.tag.track, music_entry.tag.hash, timestamp, ))

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

    def get_entries_by_title(self, title, count=100):
        entries = []

        conn = self.connect()
        cur = conn.cursor()


        query = """SELECT e.music_entry_id, e.file_path, e.file_name, e.file_hash, e.added_on, t.music_tag_id, t.title, t.artist, t.album, t.track, t.tag_hash
                FROM music_tags t
                JOIN music_entries e ON e.music_entry_id = t.music_entry_id
                JOIN music_keywords k ON k.music_entry_id = t.music_entry_id
                WHERE t.title LIKE %s OR k.keywords LIKE %s
                LIMIT %s """

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
        conn.close()

        return entries

    def add_keyword(self, music_entry_id, keyword):
        conn = self.connect()
        cur = conn.cursor()

        query = """INSERT INTO music_keywords (music_entry_id, keywords) VALUES (%s, %s)"""

        cur.execute(query, (music_entry_id, keyword, ))

        conn.commit()
        cur.close()
        conn.close()