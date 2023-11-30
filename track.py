import requests
import re
import json
 

def spot_ID(spotify_url):
	# Define the regular expression pattern for the Spotify playlist URL
	pattern = r"https://open\.spotify\.com/track/([a-zA-Z0-9]+)(\?si=.*)?"

	# Try to match the pattern in the input text
	match = re.match(pattern, spotify_url)

	if not match:
		raise ValueError("Invalid Spotify playlist URL.")
	# Extract the playlist ID from the matched pattern
	extracted_id = match.group(1)

	return extracted_id


def download_track(track_url: str):
	"""
	Note: json_data will not be serialized by requests
		exactly as it was in the original request.
		data = '{"format":"web","url":"https://open.spotify.com/track/2RJODsiuTZqwjxWr9dwN8W"}'
		response = requests.post('https://parsevideoapi.videosolo.com/sp0tify/', headers=headers, data=data)

	Args:
		track_url (str): Spotify track URL

	Returns:
		Dict: Download link and data on track
	"""
	headers = {
		'authority': 'parsevideoapi.videosolo.com',
		'accept': 'application/json, text/javascript, */*; q=0.01',
		'accept-language': 'en-US,en;q=0.9',
		'content-type': 'application/json',
		'origin': 'https://spotidown.online',
		'referer': 'https://spotidown.online/',
		'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'cross-site',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
	}

	json_data = {
		'format': 'web',
		'url': track_url,
	}

	response = requests.post('https://parsevideoapi.videosolo.com/sp0tify/', headers=headers, json=json_data)
	print(response.json())


	return json.dumps(response.json(), indent=4)



# download_track('https://open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y')
# download_track("https://open.spotify.com/track/2oSUaquyPEbz1FmKKwwW6y?si=333ee1158a494618")