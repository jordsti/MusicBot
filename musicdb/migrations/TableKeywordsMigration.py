from ..migration import Migration


class TableKeywordsMigration(Migration):
    def __init__(self):
        Migration.__init__(self, 'TableKeywordsMigration', 1)

    def up(self, connection):
        cursor = connection.cursor()
        query = """CREATE TABLE IF NOT EXISTS `music_keywords` (
                              `music_keyword_id` int(11) NOT NULL AUTO_INCREMENT,
                              `music_entry_id` int(11) NOT NULL,
                              `keywords` TEXT NOT NULL,
                              PRIMARY KEY (`music_keyword_id`)
                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8; """

        cursor.execute(query)
        connection.commit()
        # need to add keyword of each entry
        query = """SELECT e.music_entry_id, t.title, t.artist, t.album FROM music_entries e
                JOIN music_tags t ON t.music_entry_id = e.music_entry_id"""

        cursor.execute(query)
        rows = cursor.fetchall()
        query = """INSERT INTO music_keywords (music_entry_id, keywords) VALUES (%s, %s)"""

        for row in rows:
            keyword = "{0} {1} {2}".format(row[2], row[1], row[3])
            cursor.execute(query, (row[0], keyword, ))

        connection.commit()

    def down(self, connection):
        cursor = connection.cursor()
        cursor.execute("""DROP TABLE `music_keywords` """)
        connection.commit()
