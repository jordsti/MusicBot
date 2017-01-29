from .database import Database
from .scanner import MusicScanner


class MusicDb:
	def __init__(self, root="."):
		# todo config file
		self.database = Database('musicbot', '', 'musicbot')
		self.scanner = MusicScanner()
		self.root = root

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
				except:
					print("ID3 error")
			if verbose:
				print("Scanning progress {0:.2f}% ({1}/{2})".format(progress, i, nb_entries))

			i += 1
		if verbose:
			print("Scanning complete")

	def search(self, title):
		return self.database.get_entries_by_title(title)
<<<<<<< HEAD

	def search_album(self, album):
		return self.database.get_entries_by_album(album)
=======
>>>>>>> 0fcfa29deb178e8c1193e8db1a9e43aea31b9778
