import musicdb
root_music = "C:\\Users\\JGuerin\\Music"

if __name__ == '__main__':
    mdb = musicdb.MusicDb(root_music)
    mdb.update_database_schema()
    mdb.scan()

    entries = mdb.search("after the burial")

    for e in entries:
        print(e.tag.title)

