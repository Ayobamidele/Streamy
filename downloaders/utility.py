from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3
from mutagen.mp3 import MP3
import os
import zipfile
import requests


class WritingMetaTags():
	def __init__(self, tags, filename):
		super().__init__()
		self.tags = tags
		self.filename = filename
		self.PICTUREDATA = None
		self.url = None

	def setPIC(self):
		if self.tags.get('cover') is None:
			pass
		else:
			try:
				response = requests.get(self.tags['cover'] + "?size=1", stream=True)
				if response.status_code == 200:
					audio = ID3(self.filename)
					audio['APIC'] = APIC(
						encoding=3,
						mime='image/jpeg',
						type=3,
						desc=u'Cover',
						data=response.content
					)
					audio.save()

			except Exception as e:
				print(f"Error adding cover: {e}")

	def add_flac_cover(self):
		if self.tags.get('cover') is None:
			pass
		else:
			try:
				response = requests.get(self.tags['cover'] + "?size=1", stream=True)
				if response.status_code == 200:
					audio = MP3(self.filename, ID3=ID3)
					audio.tags.add(
						APIC(
							encoding=3,
							mime="image/jpeg",
							type=3,
							desc="Cover",
							data=response.content,
						)
					)
					audio.save(self.filename, v2_version=3, v1=2)
			except Exception as e:
				print(f"Error adding cover: {e}")

	def WritingMetaTags(self):
		try:
			# print('[*] FileName : ', self.filename)
			audio = EasyID3(self.filename)
			audio['title'] = self.tags.get('title')
			audio['artist'] = self.tags.get('artists')
			audio['album'] = self.tags.get('album', '')
			audio['date'] = self.tags.get('releaseDate','')
			audio.save()
			self.setPIC()
			self.add_flac_cover()

		except Exception as e:
			raise e
			print(f'Error {e}')




def zip_folder(folder_path):
	zip_path = os.path.join(folder_path, os.path.basename(folder_path) + '.zip')
	with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for root, dirs, files in os.walk(folder_path):
			for file in files:
				file_path = os.path.join(root, file)
				if file_path != zip_path:  # Avoid adding the zip file itself
					zipf.write(file_path, os.path.relpath(file_path, folder_path))
	return zip_path

def create_folder(folder_path):
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)