import requests
from fake_headers import Headers
from requests import get
import json
import eyed3

class Spotify:
	
	def __init__(self):
		self.headers = Headers(os="mac", headers=True).generate()

	def get_playlist(self, url: str):
		try:
			response = requests.get('https://api.spotifydown.com/trackList/playlist/37i9dQZF1DX5Ejj0EkURtP', headers=self.headers)
			track_list = response.json()
			return json.dumps(track_list, indent=4)
		except Exception as error:
			print(f"Got this error {error}")

playlist = Spotify()
print(playlist.get_playlist("https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=9842813578e2439f"))

# audiofile = eyed3.load("song.mp3")
# audiofile.tag.artist = "Token Entry"
# audiofile.tag.album = "Free For All Comp LP"
# audiofile.tag.album_artist = "Various Artists"
# audiofile.tag.title = "The Edge"
# audiofile.tag.track_num = 3

# audiofile.tag.save()