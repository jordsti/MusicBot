import musicdb
root_music = "/media/music"

if __name__ == '__main__':
    mdb = musicdb.MusicDb(root_music)
    mdb.scan()
    entries = mdb.search('fight for your right')
    for e in entries:
        print(e.tag.title)
        print(e.hash)
