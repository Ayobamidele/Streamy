from main import MusicScraper
from track import download_track
from album import AlbumScraper
import os

def test_Playlist():
	SPOTIFY_PLAYLIST_LINKS = ['https://open.spotify.com/playlist/37i9dQZF1DWUHcUDX0za7N?si=240a3a4a1c51409b']#'https://open.spotify.com/playlist/37i9dQZF1E39bzrYCYwDb7?si=9f91c756a3d648ff']


	for SPOTIFY_PLAYLIST_LINK in SPOTIFY_PLAYLIST_LINKS:
		"""Download all the playlists"""
		try:
			OFFSET_VARIABLE = 0  # <-- Change to start from x number of songs
			music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

			scraper = MusicScraper()
			ID = scraper.returnSPOT_ID(SPOTIFY_PLAYLIST_LINK)
			scraper.scrape_playlist(SPOTIFY_PLAYLIST_LINK, music_folder)
		except Exception as error:
			print("[*] ERROR OCCURRED. MISSING PLAYLIST LINK !\n\n\n", error)


def test_Album():
	SPOTIFY_ALBUM_LINKS = ['https://open.spotify.com/album/5EUgcfO5OWxnniHR3QYFcK?si=8JoLyXstRP6qwy7ciEznsw']
	for SPOTIFY_ALBUM_LINK in SPOTIFY_ALBUM_LINKS:
		"""Download all the playlists"""
		try:
			OFFSET_VARIABLE = 0  # <-- Change to start from x number of songs
			music_folder = os.path.join(os.getcwd(), "music")  # Change this path to your desired music folder

			scraper = AlbumScraper(SPOTIFY_ALBUM_LINK)
			ID = scraper.spot_ID()
			scraper.scrape_download()
		except Exception as error:
			print("[*] ERROR OCCURRED. MISSING ALBUM LINK !\n\n\n", error)

# test_Album()

def test_track():
	"""Download the track"""
	try:
		result = download_track('https://open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y')
		print(result)
	except Exception as error:
		print("[*] ERROR OCCURRED. MISSING TRACK LINK !\n\n\n", error)


# test_Album()