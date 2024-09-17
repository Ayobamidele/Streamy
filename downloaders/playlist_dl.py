import requests
import random
import os
import re
import string
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from downloaders.utility import WritingMetaTags, zip_folder, create_folder
import concurrent.futures
from tqdm import tqdm


from concurrent.futures import ThreadPoolExecutor


class PlaylistScraper:
	def __init__(self, link):
		super(PlaylistScraper, self).__init__()
		self.counter = 0  # Initialize the counter to zero
		self.session = requests.Session()
		retries = Retry(total=5, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
		self.session.mount('https://', HTTPAdapter(max_retries=retries))
		self.link = link
		self.upload = True
		self.playlist_folder_path = ""

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

	def get_PlaylistMetadata(self, Playlist_ID):
		# The 'get_PlaylistMetadata' function from your scraper code
		URL = f'https://api.spotifydown.com/metadata/playlist/{Playlist_ID}'
		headers = {
			'authority': 'api.spotifydown.com',
			'method': 'GET',
			'path': f'/metadata/playlist/{Playlist_ID}',
			'scheme': 'https',
			'origin': 'https://spotifydown.com',
			'referer': 'https://spotifydown.com/',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
		}
		meta_data = self.session.get(headers=headers, url=URL)
		if meta_data.status_code == 200:
			return meta_data.json()['title'] + ' - ' + meta_data.json()['artists']
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

	def V2catch(self, SONG_ID):
		## Updated .. .19TH OCTOBER 2023
		yt_id = self.get_ID(SONG_ID)

		domain = ["co.wuk.sh", "cobalt.snapredd.app", "cobalt2.snapredd.app"]
		target_domain = domain[random.randint(0, 2)]

		x = self.session.options(url=f'https://{target_domain}/api/json')
		if x.status_code == 204:
			par = {
				'aFormat': '"mp3"',
				'dubLang': 'false',
				'filenamePattern': '"classic"',
				'isAudioOnly': 'true',
				'isNoTTWatermark': 'true',
				'url': f'"https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{yt_id}"'
			}

			headers = {
				"authority": "cobalt.snapredd.app",
				"method": "POST",
				"path": '/api/json',
				"scheme": "https",
				"Accept": "application/json",

				'Sec-Ch-Ua': '"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
				"Dnt": '1',
				"Origin": "https://spotifydown.com",
				"Referer": "https://spotifydown.com/",
				"Sec-Ch-Ua-Mobile": "?0",
				"Sec-Fetch-Dest": "empty",
				"Sec-Fetch-Mode": "cors",
				"Sec-Fetch-Site": "cross-site",
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
			}

			file_status = self.session.post(url=f"https://{target_domain}/api/json", json=par, headers=headers)

		if file_status.status_code == 200:

			try:
				return {
					'link': file_status.json()['url'],
					'metadata': None
				}
			except:
				return None
		print('[*] Status Code : ', x.status_code, x.content)
		return None

	def V4catch(self, SONG_ID):
			## Updated .. .19TH OCTOBER 2023
		# yt_id = self.get_ID(SONG_ID)

		# domain = ["co.wuk.sh", "cobalt2.snapredd.app"]
		# target_domain = domain[random.randint(0,len(domain) - 1)]
		headers = {
			"authority": "api.spotifydown.com",
			"method": "POST",
			"path": f'/download/{SONG_ID}',
			"scheme": "https",
			"Accept": "*/*",

			'Sec-Ch-Ua':'"Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"',
			"Dnt": '1',
			"Origin": "https://spotifydown.com",
			"Referer": "https://spotifydown.com/",
			"Sec-Ch-Ua-Mobile": "?0",
			"Sec-Fetch-Dest": "empty",
			"Sec-Fetch-Mode": "cors",
			"Sec-Fetch-Site": "cross-site",
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
		}

		## Updated .. .29TH OCTOBER 2023
		x = self.session.get(url = f'https://api.spotifydown.com/download/{SONG_ID}', headers=headers)

		# if x.status_code == 200:

		#     # par = {
		#     #     'aFormat':'"mp3"',
		#     #     'dubLang':'false',
		#     #     'filenamePattern':'"classic"',
		#     #     'isAudioOnly':'true',
		#     #     'isNoTTWatermark':'true',
		#     #     'url':f'"https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{yt_id}"'
		#     # }

		#     file_status = self.session.post(url=f"https://{target_domain}/api/json", json=par, headers=headers)
		# print('[*] Data Gathered : ', str(x.content))
		if x.status_code == 200:

			try:
				return {
					'link' : x.json()['link'],
					'metadata' : None
				}
			except:
				return {
					'link' : None,
					'metadata' : None
				}

		return None

	def get_spotify_id(self):
			# # The 'returnSPOT_ID' function from your scraper code
			# Define the regular expression pattern for the Spotify playlist URL
			pattern = r"https://open\.spotify\.com/playlist/([a-zA-Z0-9]+)"

			# Try to match the pattern in the input text
			match = re.match(pattern, self.link)

			if not match:
				raise ValueError("Invalid Spotify playlist URL.")
			# Extract the playlist ID from the matched pattern
			extracted_id = match.group(1)

			return extracted_id

	def increment_counter(self):
		self.counter += 1

	def construct_SONG_META(self, song):
		try:
			# Extract relevant metadata from the song dictionary
			title = song['title']
			artists = song['artists']

			# Remove punctuation from title and artists
			clean_title = title.translate(str.maketrans('', '', string.punctuation))
			clean_artists = artists.translate(str.maketrans('', '', string.punctuation))

			# Construct filename and filepath
			filename = f"{clean_title} - {clean_artists}.mp3"
			filepath = os.path.join(self.playlist_folder_path, filename)

			# Set up other metadata (customize this part)
			SONG_META = {
				'title': title,
				'artists': artists,
				'file_path': filepath,
				'file_name': filename
			}

			return SONG_META
		except Exception as e:
			print(f"Error setting up SONG_META: {e}")
			return None

	def get_DL_LINK(self, song):
		V2METHOD = self.V4catch(song['id'])
		DL_LINK = V2METHOD.get('link')
		if DL_LINK:
			print('Stage One')
			return DL_LINK
		
		V2METHOD = self.V2catch(song['id'])
		DL_LINK = V2METHOD.get('link')
		if DL_LINK:
			print('Stage Two')
			return DL_LINK
		# If V2catch fails, try the YouTube method
		print('Stage Two: Playlist ID prep for YouTube')
		yt_id = self.get_ID(song['id'])
		if yt_id:
			data = self.generate_Analyze_id(yt_id)
			try:
				DL_ID = data['links']['mp3']['mp3128']['k']
				DL_DATA = self.generate_Conversion_id(data['vid'], DL_ID)
				print("Stage Three: YouTube ID found:", yt_id)
				DL_LINK = DL_DATA.get('dlink')
				return DL_LINK
			except Exception as NoLinkError:
				CatchMe = self.errorcatch(song['id'])
				DL_LINK = CatchMe if CatchMe else None
				return DL_LINK
		else:
			print('[*] No data found for:', song)
			return None

	def download_chunk(self, DL_LINK, filepath):
		try:
			link = self.session.get(DL_LINK, stream=True)
			total_size = int(link.headers.get('content-length', 0))
			block_size = 1024  # 1 Kilobyte
			downloaded = 0

			with open(filepath, "wb") as f:
				for data in link.iter_content(block_size):
					f.write(data)
					downloaded += len(data)

			print(downloaded, total_size)
			# Verify if the downloaded size matches the expected total size
			# if downloaded != total_size:
			# 	print(f"Downloaded size ({downloaded} bytes) does not match expected total size ({total_size} bytes). Re-downloading...")
			# 	return self.download_chunk(DL_LINK, filepath)  # Recursive re-download
   

			print("Saved", os.path.basename(filepath))
			return True
		except Exception as e:
			print(f"Error downloading chunk: {e}")
			return False

	def parallel_download(self, DL_LINK, filepath):
		with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
			futures = []
			for _ in range(5):  # Adjust the number of parallel downloads as needed
				future = executor.submit(self.download_chunk, DL_LINK, filepath)
				futures.append(future)

			# Wait for all downloads to complete
			concurrent.futures.wait(futures)

		return all(f.result() for f in futures)

 
	def download_song(self, DL_LINK, song_meta):
		try:
			if DL_LINK is not None:
				filepath = song_meta.get('file_path')
				link = self.session.get(DL_LINK, stream=True)
				total_size = int(link.headers.get('content-length', 0))
				block_size = 1024  # 1 Kilobyte
				downloaded = 0
				print(f"Downloading {song_meta.get('file_name')}")
				with open(filepath, "wb") as f:
					for data in tqdm(link.iter_content(block_size), total=total_size // block_size, unit='KB', desc=os.path.basename(filepath)):
						f.write(data)
						downloaded += len(data)                
				print(f"Downloaded {os.path.basename(filepath)}")
				songTag = WritingMetaTags(tags=song_meta, filename=filepath)
				songTag.WritingMetaTags()
				return True
			else:
				print('[*] No Download Link Found.')
				pass
		except Exception as e:
			print(f"Error downloading song: {e}")
			return False
	
	
		
	def playlist_download(self):
		# This part of the code is responsible for setting up the folder structure for downloading the
		# playlist. Here's a breakdown of what it does:
		playlist_ID = self.get_spotify_id()
		PlaylistName = self.get_PlaylistMetadata(playlist_ID)
		print('Playlist Name : ', PlaylistName)
		ran_loc = str(random.randint(1000000, 9999999))

		# The code snippet `music_folder = os.path.join(os.getcwd(), "tmp", "music", 'playlists', ran_loc,
		# f'{playlist_ID}')` is creating a folder path by joining multiple directory names together. Here's a
		# breakdown of what each part of the code is doing:
		music_folder = os.path.join(os.getcwd(), "tmp", "music", 'playlists', ran_loc, f'{playlist_ID}')
		create_folder(music_folder)

		try:
			FolderPath = ''.join(e for e in PlaylistName if e.isalnum() or e in [' ', '_'])
			self.playlist_folder_path = os.path.join(music_folder, FolderPath)
		except:
			self.playlist_folder_path = music_folder

		create_folder(self.playlist_folder_path)

		Playlist_Link = f'https://api.spotifydown.com/trackList/playlist/{playlist_ID}'
		offset_data = {}
		offset = 0
		offset_data['offset'] = offset
		headers = {
					'authority': 'api.spotifydown.com',
					'method': 'GET',
					'path': f'/trackList/playlist/{playlist_ID}',
					'scheme': 'https',
					'accept': '*/*',
					'dnt': '1',
					'origin': 'https://spotifydown.com',
					'referer': 'https://spotifydown.com/',
					'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
					'sec-ch-ua-mobile': '?0',
					'sec-ch-ua-platform': '"Windows"',
					'sec-fetch-dest': 'empty',
					'sec-fetch-mode': 'cors',
					'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
				}
		while offset is not None:
			response = self.session.get(url=Playlist_Link, params=offset_data, headers=headers)
			if response.status_code == 200:
				tracks = response.json()['trackList']
				page = response.json()['nextOffset']
				print("*" * 100)
				with ThreadPoolExecutor(max_workers=len(tracks)) as executor:
					executor.map(lambda track: self.download_song(self.get_DL_LINK(track), self.construct_SONG_META(track)), tracks)
				print("All files downloaded. Hello!")
			if page is not None:
				offset_data['offset'] = page
				response = self.session.get(url=Playlist_Link, params=offset_data, headers=headers)
			else:
				print("*" * 100)
				print('[*] Download Complete!')
				print("*" * 100)
				zipped_file = zip_folder(music_folder)
				print(f"File Zipped !!!\n\n {zipped_file}")
				return zipped_file




def playlist_download(url: str):
	playlist = PlaylistScraper(url)
	playlist = playlist.playlist_download()
	if playlist is not None:
		return playlist
	else:
		return False



# print(playlist_download("https://open.spotify.com/playlist/1Iw0SSR2EZs5EtCv9hKF2o?si=850ebe60bdfc487a"))