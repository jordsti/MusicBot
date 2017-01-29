import hashlib
from mutagen.easyid3 import EasyID3


class MusicTag:
    def __init__(self):
        self.id = 0
        self.title = ""
        self.album = ""
        self.artist = ""
        self.track = 0
        self.hash = ""

    def generate_hash(self):
        hasher = hashlib.md5()
        hasher.update("{0}{1}{2}{3}".format(self.title, self.artist, self.album, self.track).encode("utf8"))
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


        try:
            self.tag.track = int(self.try_get_tag('tracknumber', m))
        except:

            # try to parse the track number from the file name
            import re
            title_re = re.compile("""(?P<number>[0-9]{1,3}) ?- ?.+\.mp3""")
            m = title_re.match(self.filename)
            if m:
                self.tag.track = int(m.group("number"))
            else:
                print("Track number not found in tag")

        self.tag.generate_hash()

    def try_get_tag(self, tag_name, id3):
        try:
            return id3[tag_name][0]
        except:
            return ""