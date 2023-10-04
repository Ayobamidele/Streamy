import requests
from fake_headers import Headers
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import mutagen
from tqdm import tqdm
import os
import shutil
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter, Retry
import json
import eyed3
import time
import re



headers = {
	"authority": "api.spotifydown.com",
	"accept": "*/*",
	"accept-language": "en-US,en;q=0.9",
	"origin": "https://spotifydown.com",
	"referer": "https://spotifydown.com/",
	"sec-ch-ua": '"Microsoft Edge";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
	"sec-ch-ua-mobile": "?0",
	"sec-ch-ua-platform": '"Windows"',
	"sec-fetch-dest": "empty",
	"sec-fetch-mode": "cors",
	"sec-fetch-site": "same-site",
	"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36",
}

alt_headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0',
	'Accept': 'application/json, text/plain, */*',
	'Accept-Language': 'en-US,en;q=0.5',
	# 'Accept-Encoding': 'gzip, deflate, br',
	'Referer': 'https://spotifymusicdownloader.com/',
	'Origin': 'https://spotifymusicdownloader.com',
	'Connection': 'keep-alive',
	'Sec-Fetch-Dest': 'empty',
	'Sec-Fetch-Mode': 'cors',
	'Sec-Fetch-Site': 'cross-site',
}


def assign_attributes(
	song: str,
	title: str,
	artists: str,
	album_art: str,
	album_title: str,
	album_artist: str,
	releaseDate: str,
):
	## add the image to the album art
	album_art = os.path.join('media', album_art)

	audio = MP3(song, ID3=ID3)
	audio.tags.add(
		APIC(
			encoding=3,
			mime="image/jpeg",
			type=3,
			desc="Cover",
			data=open(album_art, "rb").read(),
		)
	)
	audio.save(song, v2_version=3, v1=2)

	audiofile = eyed3.load(song)
	audiofile.tag.artist = artists
	audiofile.tag.album = album_title
	audiofile.tag.album_artist = album_artist
	audiofile.tag.title = title
	audiofile.tag.year = releaseDate

	audiofile.tag.save()


def download_album_art(image_url):
	# Send a HTTP request to the URL of the image
	response = requests.get(image_url)

	# Check if the request was successful
	if response.status_code == 200:
		# Make sure the 'media' directory exists; if not, create it
		if not os.path.exists('media'):
			os.makedirs('media')

		# Define the initial path where you want to save the image
		path = os.path.join('media', 'image.jpg')

		# If a file with the same name already exists, append a number to the file name
		i = 1
		while os.path.exists(path):
			base, ext = os.path.splitext(path)
			path = base + str(i) + ext
			i += 1

		# Open file in binary mode and write the response content into it
		with open(path, "wb") as file:
			file.write(response.content)

	# Return the name of the file
	return os.path.basename(path)







class Spotify:
	def __init__(self):
		head =Headers(os="mac", headers=True).generate()

		head.update({"authority": "api.spotifydown.com",
					"origin": "https://spotifydown.com",
					"referer": "https://spotifydown.com/",
					"Referer": "https://spotifydown.com/",
					})
		self.headers = head




	def alt_download(self, url: str):
		#### Step 1
		# Get the id
		response = requests.get(
			f'https://api.fabdl.com/spotify/get?url={url}',
		)

		id = response.json()["result"]['gid']
		name = response.json()["result"]['name']
		parsed_url = urlparse(url)

		# Split the path of the URL into segments
		segments = parsed_url.path.split('/')

		# The last string after splitting by "/" is the last segment
		song_id = segments[-1]
		print("id - ",id,"\nsong id - ", song_id,"\n", "name - ", name)
		##### Step 2
		#  use id to get id

		response = requests.get(f'https://api.fabdl.com/spotify/mp3-convert-task/{id}/{song_id}', headers=alt_headers)
		# print(json.dumps(response.json(), indent=5))
		process_id = response.json()["result"]['tid']
		download_url = response.json()["result"]['download_url']

		print("new id - ",process_id,"\n download url -", download_url)

		###### Step 3
		#   Start the process

		response = requests.get(
			f'https://api.fabdl.com/spotify/mp3-convert-progress/{process_id}',
			headers=headers,
		)

		print(json.dumps(response.json(), indent=5))

		####### Step 4
		# Secure the download


		def download_mp3(url, filename):
			response = requests.get(url, headers=alt_headers)
			with open(filename, 'wb') as file:
				file.write(response.content)

		# Usage
		song = re.sub(r'[\\/*?:"<>|]', "", f'{name}.mp3')
		download_mp3(f'https://api.fabdl.com{download_url}', song)




	def download_file_with_progress(self, url: str):
		request = requests.Session()

		retries = Retry(total=5,
					backoff_factor=0.1,
					status_forcelist=[ 500, 502, 503, 504 ])

		request.mount('http://', HTTPAdapter(max_retries=retries))
		
		# Parse the URL
		parsed_url = urlparse(url)

		# Split the path of the URL into segments
		segments = parsed_url.path.split('/')

		# The last string after splitting by "/" is the last segment
		song_id = segments[-1]

		# Get download information for song
		response = request.get("https://api.spotifydown.com/download/" + song_id)
		data = response.json()

		# # Get Metadata
		metadata = data.get("metadata")

		# # Get Song title
		title = metadata.get('title')
		print(f"starting download for {title}")

		# # Call the function with the URL of the image you want to download
		album_art = download_album_art(metadata.get("cover",""))

		# # Get Download Link
		download_url = data.get("link")
		print(download_url)
		song = title + ".mp3"
		song = re.sub(r'[\\/*?:"<>|]', "", song)
		if os.path.exists(song):
		    print(f"The file {song} already exists.")
		    return
		# # Start Download
		try:
			print("Going main stream")
			download_response = request.get(download_url,headers=headers, stream=True)
			# Get the total file size
			file_size = int(download_response.headers.get("Content-Length", 0))

			# # Create a progress bar

			progress = tqdm(
				download_response.iter_content(1024),
				f"Downloading {song}",
				total=file_size,
				unit="B",
				unit_scale=True,
				unit_divisor=1024,
			)
			with open(song, "wb") as f:
				for data in progress.iterable:
					f.write(data)
					progress.update(len(data))

		except Exception as error:
			print("Going alt")
			try:
				def download_file(url, filename):
					backoff_time = 3
					max_backoff_time = 120

					while True:
						try:
							response = requests.get(url, timeout=5)
							response.raise_for_status()  # Raise an exception if the status is not 200

							with open(filename, 'wb') as f:
								f.write(response.content)

							print(f"Downloaded file successfully.")
							break

						except (requests.exceptions.RequestException, Exception) as e:
							print(f"Error occurred: {e}. Retrying in {backoff_time} seconds...")

							time.sleep(backoff_time)
							backoff_time = min(backoff_time * 2, max_backoff_time)
				download_file(download_url, song)
			except:
				pass



		
		artists = metadata.get("artists","")
		album_title = metadata.get("album","")
		album_artist = metadata.get("artists","").split(",")[0]
		releaseDate = metadata.get("releaseDate","").split('-')[0]
		assign_attributes(song, title, artists, album_art, album_title, album_artist, releaseDate)
		# shutil.move( song, "media")


	def get_playlist(self, url: str):
		current_song_url = ""
		close = False
		try:
			params = {}

			count = 0
			songs = []

			# Parse the URL
			parsed_url = urlparse(url)

			# Split the path of the URL into segments
			segments = parsed_url.path.split('/')

			# The last string after splitting by "/" is the last segment
			playlist_id = segments[-1]

			url = f"https://api.spotifydown.com/trackList/playlist/{playlist_id}"
			tries = 4
			count_tries = 0
			def get_response_json(url):
				response = requests.get(
					url,
					headers=headers,
					params=params,
					timeout=3
				)
				# print(response, response.text)
				result = response.json()
				return result
			while count_tries < tries :
				try:
					result = get_response_json(url)
					count_tries+=1
				except Exception as error:
					time.sleep(15)
					try:
						result = get_response_json(url)
						count_tries+=1
					except Exception as error:
						time.sleep(10)
						try:
							result = get_response_json(url)
							count_tries+=1
						except Exception as error:
							close = True 
				if not(close):       
					if type(result.get("nextOffset")) is str:
						params.update({"offset": str(result.get("nextOffset"))})
						for track in result.get("trackList"):
							# print(json.dumps(track, indent=4))
							count += 1
							current_song_url = "https://open.spotify.com/track/"+track.get("id")
							songs.append(track)
					else:
						for track in result.get("trackList"):
							# print(json.dumps(track, indent=4))
							count += 1
							current_song_url = "https://open.spotify.com/track/"+track.get("id")
							songs.append(track)
					break
				else:
					break
			return songs, count
		except Exception as error:
			raise error



playlist = Spotify()
track_list, track_total = playlist.get_playlist("https://open.spotify.com/playlist/37i9dQZF1DWZ2fb6SBrzTW")
print(len(track_list), track_total)

def download_spotify(tracks):
	for track in tracks:
		try:
			print("Here 1")
			playlist.download_file_with_progress("https://open.spotify.com/track/"+track.get("id"))
		except Exception as e:
			try:
				print("Here 2")
				playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
			except Exception as e:
				print("Here 3")
				playlist.download_file_with_progress("https://open.spotify.com/track/"+track.get("id"))
				try:
					print("Here 4")
					playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
				except Exception as e:
					raise e
					# playlist.download_file_with_progress("https://open.spotify.com/track/"+track.get("id"))
				
download_spotify(track_list)
# playlist.download_file_with_progress("https://open.spotify.com/track/2IGMVunIBsBLtEQyoI1Mu7?si=4d081c88174d48ec")
# 	else:
# 		playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
# 		if track in track_list:
# 			track_list.remove(track)



# for track in track_list:
# 	try:
# 		playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
# 		if track in track_list:
# 			track_list.remove(track)
# 	except Exception as e:
# 		playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
# 		if track in track_list:
# 			track_list.remove(track)
# 	else:
# 		playlist.alt_download("https://open.spotify.com/track/"+track.get("id"))
# 		if track in track_list:
# 			track_list.remove(track)

# playlist.download_file_with_progress('https://open.spotify.com/track/42uwoFhTQ08s3YrB0riQmz?si=2374757d4a394e3e')



# playlist.alt_download("https://open.spotify.com/track/3oDFtOhcN08qeDPAK6MEQG?si=f2c93192cc2648d8")