import requests
import re
import json
import string
import random
import os
import requests
from mutagen.easyid3 import EasyID3
from mutagen.id3 import APIC, ID3


class WritingMetaTags():
	def __init__(self, tags, filename):
		super().__init__()
		self.tags = tags
		self.filename = filename
		self.PICTUREDATA = None
		self.url = None

	def setPIC(self):
		if self.tags['cover'] is None:
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

	def WritingMetaTags(self):
		try:
			# print('[*] FileName : ', self.filename)
			audio = EasyID3(self.filename)
			audio['title'] = self.tags.get('title',"")
			audio['artist'] = self.tags.get('artists',"")
			audio['album'] = self.tags.get('album',"")
			audio['date'] = self.tags.get('releaseDate',"")
			audio.save()
			self.setPIC()
			return False
		except Exception as e:
			print(f'Error {e}')
			return True


class AlbumScraper:
	def __init__(self, link, static=True, duration=None):
		super(AlbumScraper, self).__init__()
		self.counter = 0  # Initialize the counter to zero
		self.session = requests.Session()
		self.link = link
		self.static = static
		self.duration = duration
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
		pattern = r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)"
		match = re.match(pattern, self.link)
		if not match:
			raise ValueError("Invalid Spotify playlist URL.")
		extracted_id = match.group(1)
		return extracted_id
	
	def increment_counter(self):
		self.counter += 1
	
	def get_TrackMetadata(self,URL):
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
		print(response.content)
		if response.status_code == 200:
			data = response.json()
			print(data)
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
	
	
	def scrape_download(self):	
		trackID = self.spot_ID()
		track_link = f'https://api.spotifydown.com/metadata/album/{trackID}'
		trackName = self.get_TrackMetadata(f'https://api.spotifydown.com/metadata/track/{trackID}')
		print('Track Name : ', trackName.get("title"))
		# Create Folder for Track
		if self.static:
			music_folder = os.path.join(os.getcwd(), "tmp","music", 'track')
			if not os.path.exists(music_folder):
				os.makedirs(music_folder)
			
			track_folder_path = music_folder

			if not os.path.exists(track_folder_path):
				os.makedirs(track_folder_path)	

			
			print(f"[**] Downloading : ", trackName['title'], "-", trackName['artists'])
			filename = f"{trackName['id']} . " + trackName['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + trackName[
				'artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
			filepath = os.path.join(track_folder_path, filename)
		else:
			print("static")
			music_folder = os.path.join(os.getcwd(),"tmp", "music", 'track')
			if not os.path.exists(music_folder):
				os.makedirs(music_folder)
			try:
				FolderPath = ''.join(e for e in trackName.get('title') if e.isalnum() or e in [' ', '_'])
				track_folder_path = os.path.join(music_folder, FolderPath)
			except:
				track_folder_path = music_folder

			if not os.path.exists(track_folder_path):
				os.makedirs(track_folder_path)	

			
			print(f"[**] Downloading : ", trackName['title'], "-", trackName['artists'])
			filename = trackName['title'].translate(str.maketrans('', '', string.punctuation)) + ' - ' + trackName[
				'artists'].translate(str.maketrans('', '', string.punctuation)) + '.mp3'
			filepath = os.path.join(track_folder_path, filename)
		if not os.path.isfile(filepath) or self.duration != None:
			try:
				song_downloaded = True
				print(filepath,"\n got here")
				try:
					print('Stage One: Setting up Direct Method')
					V2METHOD = self.V2catch(trackName['id'])
					DL_LINK = V2METHOD['link']
					SONG_META = trackName
					SONG_META['file'] = filepath
				except:
					print('Stage Two: ID prep for Youtube')
					SONG_META = trackName
					SONG_META['file'] = filepath
					yt_id = self.get_ID(trackName['id'])
					if yt_id is not None:
						print("Stage Three: ", yt_id)
						data = self.generate_Analyze_id(yt_id)
						try:
							DL_ID = data['links']['mp3']['mp3128']['k']
							DL_DATA = self.generate_Conversion_id(data['vid'], DL_ID)
							DL_LINK = DL_DATA['dlink']
						except Exception as NoLinkError:
							CatchMe = self.errorcatch(trackName['id'])
							if CatchMe is not None:
								DL_LINK = CatchMe
					else:
						print('[*] No data found for : ', trackName.get("title"))
				if DL_LINK is not None:
					## DOWNLOAD
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
					print("Saved ", filename)
					self.increment_counter()
				else:
					print('[*] No Download Link Found.')
				if (DL_LINK is not None) & (download_complete == True):
					songTag = WritingMetaTags(tags=SONG_META, filename=filepath)
					# add track met
					songTag.WritingMetaTags()
			except Exception as error_status:
				print('[*] Error Status Code : ', error_status)
				return None

		print("*" * 100)
		print('[*] Download Complete!')
		print("*" * 100)
		full_path = r"{}".format(filepath)
		parts = full_path.split("\\")
		index = parts.index("tmp")
		subpath = parts[index + 1:]
		result = "/".join(subpath)
		return full_path, result


		
# url = 'https://open.spotify.com/album/68TQfjV32Dyaq9YRDcpirG?si=SjpMNS7wQBKlldgUbhrspw'



	

# download_track('https://open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y')
# download_track("https://open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y?si=333ee1158a494618")
# test = AlbumScraper("https:/open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y?si=333ee1158a494618")
# print(test.scrape_download())
	
def track_download(track_url: str, static: bool = True):
    track = AlbumScraper(track_url, static=static)
    track = track.scrape_download()
    if track is not None: # check if track is not None
        return True, track[1] ,track[0]
    else:
        return False, None, None

