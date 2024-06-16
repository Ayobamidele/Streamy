from downloaders.album_dl import AlbumScraper
from downloaders.playlist_dl import PlaylistScraper



def download_album(album_link):
	scraper = AlbumScraper(album_link)
	return scraper.scrape_download()


def download_playlist(playlist_link):
	scraper = PlaylistScraper()
	return scraper.scrape_playlist(playlist_link)

	
def detect_and_download(spotify_link):
	link_types = {
		'album': download_album,
		'playlist': download_playlist,
		'track': 'This is a track link.'
	}
	for link_type, action in link_types.items():
		if link_type in spotify_link:
			print(spotify_link)
			return action(spotify_link)
	return 'This is not a recognized Spotify link.'