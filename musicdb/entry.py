import hashlib
from mutagen.easyid3 import EasyID3


class MusicTag:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.album = ""
        self.artist = ""
        self.hash = ""

    def generate_hash(self):
        hasher = hashlib.md5()
        hasher.update("{0}{1}{2}".format(self.title, self.artist, self.album).encode("utf8"))
        self.hash = hasher.hexdigest()

class MusicEntry:
    def __init__(self, file_path, filename):
        self.tag = None
        self.id = 0
        self.file_path = file_path
        self.filename = filename
        self.hash = ""
        self.added_on = 0

    def hash_file(self):
        hasher = hashlib.md5()

        with open(self.file_path, 'rb') as fp:
            buf = fp.read()
            hasher.update(buf)

        self.hash = hasher.hexdigest()

    def read_tags(self):
        m = EasyID3(self.file_path)
        self.tag = MusicTag()
        self.tag.title = self.try_get_tag('title', m)
        self.tag.album = self.try_get_tag('album', m)
        self.tag.artist = self.try_get_tag('artist', m)
        self.tag.generate_hash()

    def try_get_tag(self, tag_name, id3):
        try:
            return id3[tag_name][0]
        except:
            return ""