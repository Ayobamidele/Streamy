import string
import os
import requests
import re
import random
from dotenv import load_dotenv
from downloaders.utility import WritingMetaTags, zip_folder, create_folder
import shutil

load_dotenv()


class AlbumScraper:
	def __init__(self, link):
		super(AlbumScraper, self).__init__()
		self.counter = 0  # Initialize the counter to zero
		self.session = requests.Session()
		self.link = link
		self.upload = True
		self.headers = {
			'authority': 'api.spotifydown.com',
			'accept': '*/*',
			'accept-language': 'en-US,en;q=0.9',
			'if-none-match': 'W/"8ce-XGRg7bM1V96j2btYqT46Cq1UA9o"',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"Windows"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
		}
	
	def spot_ID(self):
		# # The 'returnSPOT_ID' function from your scraper code

		# Define the regular expression pattern for the Spotify playlist URL
		pattern = r"https://open\.spotify\.com/album/([a-zA-Z0-9]+)"

		# Try to match the pattern in the input text
		match = re.match(pattern, self.link)

		if not match:
			raise ValueError("Invalid Spotify Album URL.")
		# Extract the playlist ID from the matched pattern
		extracted_id = match.group(1)

		return extracted_id
	
	def increment_counter(self):
		self.counter += 1
	
	def get_AlbumMetadata(self,URL):
		# The 'get_PlaylistMetadata' function from your scraper code
		meta_data = self.session.get(headers=self.headers, url=URL)
		if meta_data.status_code == 200:
			etag = meta_data.headers.get('ETag')
			self.headers['If-None-Match'] = etag
			return meta_data.json()
			return meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
		return None
	
	def V2catch(self,track_id):
		response = self.session.get(f'https://api.spotifydown.com/download/{track_id}', headers=self.headers)
		return response.json()
	
	def get_ID(self, yt_id):
		# The 'get_ID' function from your scraper code
		LINK = f'https://api.spotifydown.com/getId/{yt_id}'
		headers = {
			'authority': 'api.spotifydown.com',
			'method': 'GET',
			'path': f'/getId/{id}',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
			'sec-fetch-mode': 'cors',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
		}
		response = self.session.get(url=LINK, headers=headers)
		if response.status_code == 200:
			data = response.json()
			return data['id']
		return None

	def generate_Analyze_id(self, yt_id):
		# The 'generate_Analyze_id' function from your scraper code
		DL = 'https://proxy.cors.sh/https://www.y2mate.com/mates/analyzeV2/ajax'
		data = {
			'k_query': f'https://www.youtube.com/watch?v={yt_id}',
			'k_page': 'home',
			'hl': 'en',
			'q_auto': 0,
		}
		headers = {
			# 'authority': 'corsproxy.io',
			'method': 'POST',
			'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
			'sec-fetch-mode': 'cors',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
		}
		RES = self.session.post(url=DL, data=data, headers=headers)
		if RES.status_code == 200:
			return RES.json()
		return None

	def generate_Conversion_id(self, analyze_yt_id, analyze_id):
		# The 'generate_Conversion_id' function from your scraper code
		DL = 'https://corsproxy.io/?https://www.y2mate.com/mates/convertV2/index'
		data = {
			'vid': analyze_yt_id,
			'k': analyze_id,
		}
		headers = {
			'authority': 'corsproxy.io',
			'method': 'POST',
			'path': '/?https://www.y2mate.com/mates/analyzeV2/ajax',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
			'sec-fetch-mode': 'cors',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
		}
		RES = self.session.post(url=DL, data=data, headers=headers)
		if RES.status_code == 200:
			return RES.json()
		return None

	def errorcatch(self, SONG_ID):
		# The 'errorcatch' function from your scraper code
		print('[*] Trying to download...')
		headers = {
			'authority': 'api.spotifydown.com',
			'method': 'GET',
			'path': f'/download/{SONG_ID}',
			'scheme': 'https',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
		}
		x = self.session.get(headers=headers, url='https://api.spotifydown.com/download/' + SONG_ID)
		if x.status_code == 200:
			return x.json()['link']
		return None


	def delete_folder(self, folder_path):
		if os.path.exists(folder_path):
			try:
				shutil.rmtree(folder_path)
				print(f"Folder '{folder_path}' has been deleted.")
			except Exception as e:
				print(f"Error deleting folder: {e}")
		else:
			print(f"Folder '{folder_path}' does not exist.")

	def download(self):
		albumID = self.spot_ID()
		album_link = f'https://api.spotifydown.com/metadata/album/{albumID}'
		trackList_link = f'https://api.spotifydown.com/trackList/album/{albumID}'
		albumName = self.get_AlbumMetadata(album_link)
		print('Album Name : ', albumName)

		ran_loc = str(random.randint(1000000, 9999999))
		music_folder = os.path.join(os.getcwd(), "tmp", "music", 'album', ran_loc, f'{albumID}')
		create_folder(music_folder)

		try:
			FolderPath = ''.join(e for e in albumName.get('title') if e.isalnum() or e in [' ', '_'])
			album_folder_path = os.path.join(music_folder, FolderPath)
		except:
			album_folder_path = music_folder

		create_folder(album_folder_path)

		offset_data = {'offset': 0}
		while offset_data['offset'] is not None:
			response = self.session.get(url=trackList_link, params=offset_data, headers=self.headers)
			if response.status_code == 200:
				Tdata = response.json()['trackList']
				offset_data['offset'] = response.json()['nextOffset']
				print("*" * 100)
				for count, song in enumerate(Tdata):
					print(f"[*{count}*] Downloading : ", song['title'], "-", song['artists'])
					filename = song['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + song[
						'artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
					filepath = os.path.join(album_folder_path, filename)
					song['cover'] = song.get('cover', albumName.get('cover'))
					song['cover'] = albumName.get('cover') if song.get('cover') == None else song.get('cover')
					print(song)
					if not os.path.isfile(filepath):
						try:
							try:
								print('Stage One: Setting up Method')
								V2METHOD = self.V2catch(song['id'])
								DL_LINK = V2METHOD['link']
								SONG_META = song
								SONG_META['file'] = filepath
							except:
								print('Stage Two: ID prep for Youtube')
								SONG_META = song
								SONG_META['file'] = filepath
								yt_id = self.get_ID(song['id'])
								if yt_id is not None:
									print("Stage Three: ", yt_id)
									data = self.generate_Analyze_id(yt_id)
									try:
										DL_ID = data['links']['mp3']['mp3128']['k']
										DL_DATA = self.generate_Conversion_id(data['vid'], DL_ID)
										DL_LINK = DL_DATA['dlink']
									except Exception as NoLinkError:
										CatchMe = self.errorcatch(song['id'])
										if CatchMe is not None:
											DL_LINK = CatchMe
								else:
									print('[*] No data found for : ', song)

							if DL_LINK is not None:
								## DOWNLOAD
								print(count,"\n\n", DL_LINK)
								link = self.session.get(DL_LINK, stream=True)
								total_size = int(link.headers.get('content-length', 0))
								block_size = 1024  # 1 Kilobyte
								downloaded = 0
								## Save
								with open(filepath, "wb") as f:
									for data in link.iter_content(block_size):
										f.write(data)
										downloaded += len(data)
								download_complete = True
								# Increment the counter
								print("saved ", filename)
								self.increment_counter()
							else:
								print('[*] No Download Link Found.')
							if (DL_LINK is not None) & (download_complete == True):
								songTag = WritingMetaTags(tags=SONG_META, filename=filepath)
								song_meta_add = songTag.WritingMetaTags()
						except Exception as error_status:
							print('[*] Error Status Code : ', error_status)

			if offset_data['offset'] is not None:
				response = self.session.get(url=album_link, params=offset_data, headers=self.headers)
			else:
				print("*" * 100)
				print('[*] Download Complete!')
				print("*" * 100)
				zipped_file = zip_folder(music_folder)
				print(f"File Zipped !!!\n\n {zipped_file}")
				if os.getenv('FLASK_ENV').lower() == 'production':
					print("*" * 100)
					print(f'[*] Deleting "{music_folder}"')
					self.delete_folder(music_folder)
					print("*" * 100)
				return zipped_file
			break


	
def album_download(url: str):
	album = AlbumScraper(url)
	album = album.download()
	if album is not None:
		return album
	else:
		return False