from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import time
from flask_session import Session
from utitlity import detect_and_download
import os
import requests
import json
from downloaders.track import track_download
from functools import wraps
import base64
import mutagen
from mutagen.id3 import ID3, ID3NoHeaderError
from mutagen.mp3 import MP3
import eyed3
from dotenv import load_dotenv
import socket

# get the hostname of the local machine
hostname = socket.gethostname()
load_dotenv()
app = Flask(__name__)
SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


REFRESH_ENDPOINT = 'https://accounts.spotify.com/api/token'

# Global variable to store download progress
download_progress = 0

download_in_progress = []
downloaded = {}



def isMp3Valid(file_path):
	try:
		audio = eyed3.load(file_path) # load the file
		if audio is None: # file is not a valid mp3 format
			return False
		return True # file is a valid mp3 format
	except Exception as e: # file cannot be opened or read
		print(e)
		return False




def delete_corrupted_mp3(folder_path):
	#You can remove this part if you don't want the deletion part. Hope it helps
	for file, dir, files in os.walk(folder_path):
		for f in files:
			try:
				if not eyed3.load("{}/{}".format(file, f)): # use eyed3.load to check if the file is a valid mp3
					os.remove("{}/{}".format(file, f))
			except Exception as e:
				print(e)


def audio_duration(filepath): 
	audio = MP3(filepath)
	audio_info = audio.info 
	length = int(audio_info.length) 
	hours = length // 3600  # calculate in hours 
	length %= 3600
	mins = length // 60  # calculate in minutes 
	seconds = length % 60  # calculate in seconds 

	# Format the time as HH:MM:SS if hours > 0, MM:SS otherwise
	if hours > 0:
		duration = f"{hours:02d}:{mins:02d}:{seconds:02d}"
	else:
		duration = f"{mins:02d}:{seconds:02d}"

	return duration.lstrip('0') if duration[0] == '0' else duration


def refresh_token():
	data = {
		'grant_type': 'refresh_token',
		'refresh_token': session["refresh_token"]
	}
	auth_header = {
		'Authorization': 'Basic ' + base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
	}
	response = requests.post(REFRESH_ENDPOINT, data=data, headers=auth_header)
	jsonResponse = json.loads(response.content)
	for key in jsonResponse:
		if key == "access_token":
			session["access_token"] = jsonResponse[key]
		elif key == "refresh_token":
			session["refresh_token"] = jsonResponse[key]
		elif key == 'expires_in':
			session['expires_in'] = jsonResponse[key]
	return jsonResponse

def is_token_expired(token_info):
	now = int(time.time())
	return token_info['expires_at'] - now 

def require_valid_token(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		token_info = {
			'access_token': session['access_token'],
			'expires_at': session['expires_in']
		}
		if is_token_expired(token_info):
			token_info = refresh_token()
		return f(*args, **kwargs)
	return decorated_function

@app.route("/download/update")
def update_download_progress():
	url = request.get_json().get("url")


def download_file(url, local_filename):
	global download_progress
	with requests.get(url, stream=True) as r:
		r.raise_for_status()
		total_size = int(r.headers.get("content-length", 0))
		block_size = 1024  # 1 Kbyte
		num_blocks = total_size // block_size

		with open(local_filename, "wb") as f:
			for chunk in r.iter_content(block_size):
				if chunk:
					f.write(chunk)
					download_progress += 1
					print(f"Progress: {download_progress / num_blocks * 100}%")


@app.route("/progress")
def progress():
	global download_progress
	# print('Hello')
	return jsonify({"progress": download_progress})


@app.route("/test", methods=["GET"])
def test():
	return render_template("test.html")


def compare_durations(actual_duration, expected_duration):
	# Split the song lengths into hours, minutes, and seconds
	actual_duration = actual_duration.split(':')
	expected_duration = expected_duration.split(':')

	# Pad missing parts with zeros
	while len(actual_duration) < 3:
		actual_duration.insert(0, '0')
	while len(expected_duration) < 3:
		expected_duration.insert(0, '0')

	# Convert the song lengths to seconds
	actual_duration = int(actual_duration[0]) * 3600 + int(actual_duration[1]) * 60 + int(actual_duration[2])
	expected_duration = int(expected_duration[0]) * 3600 + int(expected_duration[1]) * 60 + int(expected_duration[2])

	# Compare the song lengths
	if actual_duration >= expected_duration:
		print("Actual song duration is longer than or equal to expected song duration.")
		return True
	else:
		print("Actual song duration is shorter than expected song duration.")
		return False





@app.template_filter("track_folders_exist")
def track_folders_exist(folders):
	track_name = folders[0]
	track_url = folders[1]
	folder_name = folders[2]
	track_duration = folders[3]
	folder_name = "".join(e for e in folder_name if e.isalnum() or e in [" ", "_"])
	folder_path = os.path.join(os.getcwd(), "music", "album", folder_name)
	if os.path.exists(folder_path):
		"""If it has been downloaded"""
		for file_name in os.listdir(folder_path):
			if os.path.isfile(os.path.join(folder_path, file_name)):
				file_path = os.path.join(folder_path, file_name)
				try:
					audio = ID3(file_path)
					file_name = audio['TIT2'].text[0]
				except ID3NoHeaderError:
					audio = mutagen.File(file_path) # load the mp3 file
					file_name = audio["TIT2"].text[0]
				if file_name == track_name:
					if not(compare_durations(audio_duration(file_path), track_duration)):
						if not(isMp3Valid(file_path)): 
							print(f"{file_name} duration of song is - {audio_duration(file_path)} and it is expected to be {track_duration}")
							return f"""
										<button class="focus:outline-none pr-4 group download-track" data-track={track_url} onclick="saveSong(this)" type="button">
											<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 48 48"><g fill="none" stroke="currentColor" stroke-width="4"><path stroke-linejoin="round" d="M24 5L2 43h44z" clip-rule="evenodd"/><path stroke-linecap="round" d="M24 35v1m0-17l.008 10"/></g></svg>
										</button>
									"""
		return """	
					<button class="focus:outline-none pr-4 group download-track" type="button">
						<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19L21 7l-1.41-1.41z"/></svg>
					</button>
				"""
	else:
		if track_url in download_in_progress:
			svg = """
						<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" class="spinner_P7sC"/></svg>
				"""
			return f"""
				<button class="focus:outline-none pr-4 group download-track"  type="button">
					{svg}
				</button>"""
		return f"""
					<button class="focus:outline-none pr-4 group download-track" data-track={track_url} onclick="saveSong(this)" type="button">
						<svg class="w-4 h-4 group-hover:text-green-600" viewBox="0 0 24 24" fill="none"
						stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						<path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5 5-5-5M12 12.8V2.5" /></svg>
					</button>"""


@app.template_filter("album_folders_exist")
def album_folders_exist(folders):
	folder_name = folders[0]
	folder_url = folders[1]
	tracks = folders[2]
	total_tracks = folders[3]
	incomplete = False
	folder_name = "".join(e for e in folder_name if e.isalnum() or e in [" ", "_"])
	folder_path = os.path.join(os.getcwd(), "music", "album", folder_name)
	if os.path.exists(folder_path):
		for file_name in os.listdir(folder_path):
			file_path = os.path.join(folder_path, file_name)
			for i in tracks:
				if os.path.isfile(file_path):
					try:
						audio = ID3(os.path.join(folder_path, file_name))
						file_name = audio['TIT2'].text[0]
					except Exception as error:
						file_name = None
					if file_name == i.get('track_title'):
						if audio_duration(file_path) < i.get('track_duration') and total_tracks != len(os.listdir(folder_path)):
							print("Inside duration", file_name)
							return f"""<button data-url="{ folder_url }" class="text-gray-500 hover:text-gray-900 download flex">
										<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 48 48"><g fill="none" stroke="currentColor" stroke-width="4"><path stroke-linejoin="round" d="M24 5L2 43h44z" clip-rule="evenodd"/><path stroke-linecap="round" d="M24 35v1m0-17l.008 10"/></g></svg>
										<span class="pl-2">Download Album Again. Some parts are missing</span>
								</button>"""
		return f"""<button data-url="{ folder_url }" class="text-gray-500 hover:text-gray-900 flex">
						<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19L21 7l-1.41-1.41z"/></svg>		
						<span class="pl-2 p-0 my-auto">Downloaded Album</span>
					</button>"""
	else:
		if folder_url in download_in_progress:
			svg = """
						<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" class="spinner_P7sC"/></svg>
				"""
			return f"""<button data-url="{ folder_url }" class="text-gray-500 hover:text-gray-900 flex">
						{svg}
						<span class="pl-2 mx-auto">Downloading Album</span>
					</button>"""
		return f"""<button data-url="{ folder_url }" class="text-gray-500 hover:text-gray-900 download flex">
						<svg class="w-4 h-4 group-hover:text-green-600" viewBox="0 0 24 24" fill="none"
							stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							<path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5 5-5-5M12 12.8V2.5" /></svg>
						<span class="pl-2">Download Album</span>
					</button>"""


@app.template_filter("folders_exist")
def folders_exist_filter(folders):
	folder_name = folders[0]
	folder_type = folders[1]
	folder_url = folders[2]
	folder_name = "".join(e for e in folder_name if e.isalnum() or e in [" ", "_"])
	folder_path = os.path.join(os.getcwd(), "music", folder_type, folder_name)
	if os.path.exists(folder_path):
		for file_name in os.listdir(folder_path):
			if os.path.getsize(os.path.join(folder_path, file_name)) == 0:
				return f"""<button data-url="{folder_url}" class="text-gray-500 hover:text-gray-900 download">
								<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 36 36">
								<path fill="black" d="M31 31H5a1 1 0 0 0 0 2h26a1 1 0 0 0 0-2Z" class="clr-i-outline--alerted clr-i-outline-path-1--alerted"/>
								<path fill="black" d="m18 29.48l10.61-10.61a1 1 0 0 0-1.41-1.41L19 25.65V5a1 1 0 0 0-2 0v20.65l-8.19-8.19a1 1 0 1 0-1.41 1.41Z" class="clr-i-outline--alerted clr-i-outline-path-2--alerted"/>
								<path fill="black" d="M26.85 1.14L21.13 11a1.28 1.28 0 0 0 1.1 2h11.45a1.28 1.28 0 0 0 1.1-2l-5.72-9.86a1.28 1.28 0 0 0-2.21 0Z" class="clr-i-outline--alerted clr-i-outline-path-3--alerted clr-i-alert"/>
								<path fill="none" d="M0 0h36v36H0z"/>
								</svg>
						</button>"""
		return '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><path fill="black" d="M21 7L9 19l-5.5-5.5l1.41-1.41L9 16.17L19.59 5.59L21 7Z"/></svg>'
	else:
		if folder_url in download_in_progress:
			return '<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><style>.spinner_P7sC{transform-origin:center;animation:spinner_svv2 .75s infinite linear}@keyframes spinner_svv2{100%{transform:rotate(360deg)}}</style><path d="M10.14,1.16a11,11,0,0,0-9,8.92A1.59,1.59,0,0,0,2.46,12,1.52,1.52,0,0,0,4.11,10.7a8,8,0,0,1,6.66-6.61A1.42,1.42,0,0,0,12,2.69h0A1.57,1.57,0,0,0,10.14,1.16Z" class="spinner_P7sC"/></svg>'
		return f"""<button data-url="{folder_url}" class="text-gray-500 hover:text-gray-900 download">
											<svg
												xmlns="http://www.w3.org/2000/svg" width="32" height="32"
												viewBox="0 0 256 256">
												<path fill="currentColor"
													d="M222 152v56a14 14 0 0 1-14 14H48a14 14 0 0 1-14-14v-56a6 6 0 0 1 12 0v56a2 2 0 0 0 2 2h160a2 2 0 0 0 2-2v-56a6 6 0 0 1 12 0Zm-98.24 4.24a6 6 0 0 0 8.48 0l40-40a6 6 0 0 0-8.48-8.48L134 137.51V40a6 6 0 0 0-12 0v97.51l-29.76-29.75a6 6 0 0 0-8.48 8.48Z" />
											</svg>
										</button>"""


@app.route("/search", methods=["GET"])
@require_valid_token
def search_form():
	data = session.get("data", "No result Found")
	result = request.args.get("result", False)
	return render_template("search.html", result=result, data=data)


@app.route("/download", methods=["POST"])
def download():
	url = request.args.to_dict().get("url")  # Convert the query parameters to a dictionary
	type = "Done"
	download_in_progress.append(url)
	print(type)
	detect_and_download(url)
	print("Data received: {}".format(type))
	download_in_progress.remove(url)
	return {"message": "Downloaded"}, 200


@app.route("/tracks")
def tracks():
	id = "2RJODsiuTZqwjxWr9dwN8W"
	response = requests.get(
		url=f"https://api.spotify.com/v1/tracks/{id}",
		headers={"Authorization": "Bearer " + session["access_token"]},
	)
	jsonResponse = json.loads(response.content)
	return jsonResponse


# home
@app.route("/")
def home():
	return render_template("home.html")


# authorize
@app.route("/authorize")
def authorize():
	# user-library-read is the "scope authorization" to retrieve infos like ALBUMS
	# redirect_uri is encoded, but correspond to http://localhost:5000/tokens
	AUTHORIZE_URL = (
		"https://accounts.spotify.com/authorize?response_type=code&client_id="
		+ SPOTIFY_CLIENT_ID
		+ "&scope=user-library-read&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Ftokens%2F"
	)
	return redirect(AUTHORIZE_URL)


# tokens
@app.route("/tokens/")
def tokens():
	authorizationCode = request.args.get("code")
	response = requests.post(
		url="https://accounts.spotify.com/api/token",
		data={
			"code": str(authorizationCode),
			"redirect_uri": f"http://{hostname}:5000/tokens/",
			"grant_type": "authorization_code",
			"client_id": SPOTIFY_CLIENT_ID,
			"client_secret": SPOTIFY_CLIENT_SECRET,
		},
	)

	jsonResponse = json.loads(response.content)
	print(jsonResponse)

	for key in jsonResponse:
		if key == "access_token":
			session["access_token"] = jsonResponse[key]
		elif key == "refresh_token":
			session["refresh_token"] = jsonResponse[key]
		elif key == 'expires_in':
			session['expires_in'] = jsonResponse[key]
	return redirect(url_for("search_form"))





@app.route('/protected', methods=['GET'])
@require_valid_token
def protected_route():
	return jsonify({'message': 'You accessed a protected route!'})


@app.route("/search_results", methods=["POST"])
@require_valid_token
def search():
	response = requests.get(
		url="https://api.spotify.com/v1/search",
		params={
			"q": request.form.get("query"),
			"type": "album,playlist,track,artist",
			"include_external": "audio",
		},
		headers={"Authorization": "Bearer " + session["access_token"]},
	)
	try:
		jsonResponse = response.json()
		albums = jsonResponse.get("albums").get("items")
		albums = [
			{
				"id": i.get("id"),
				"name": i.get("name"),
				"image": i.get("images")[0].get("url") if i.get("images") else False,
				"url": i.get("external_urls").get("spotify"),
				"type": "album",
			}
			for i in albums
			if i.get("name")
		]
		tracks = jsonResponse.get("tracks").get("items")
		tracks = [
			{
				"id": i.get("id"),
				"name": i.get("name"),
				"image": i.get("album").get("images")[0].get("url")
				if i.get("album")
				else False,
				"url": i.get("external_urls").get("spotify"),
			}
			for i in tracks
			if i.get("name")
		]
		playlists = jsonResponse.get("playlists").get("items")
		playlists = [
			{
				"id": i.get("id"),
				"name": i.get("name"),
				"image": i.get("images")[0].get("url") if i.get("images") else False,
				"url": i.get("external_urls").get("spotify"),
			}
			for i in playlists
			if i.get("name")
		]
		data = {"albums": albums, "tracks": tracks, "playlists": playlists}
		session["data"] = data
		print(data)
	except Exception as e:
		pass
	return redirect(url_for("search_form", result=True))


def find_file(directory, filename):
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.split('.')[0] == filename:
				filepath = os.path.join(root, file)
				full_path = r"{}".format(filepath)
				# Find the index of "static" in the string
				index = full_path.find(r'\static')
				if index != -1:
					# Add 8 to the index to account for the length of the string "\static\"
					return url_for("static", filename=full_path[index + 8:].replace('\\','/'))
	return False





def calculate_duration(duration_ms):
	# Convert milliseconds to seconds
	duration_s = duration_ms / 1000
	# Calculate minutes and remaining seconds
	minutes = int(duration_s // 60)
	seconds = int(duration_s % 60)
	# Add a leading zero to seconds if it's less than 10
	seconds = str(seconds).zfill(2)
	return f"{minutes}:{seconds}"


def get_tracks(url):
	tracks = []
	while url:
		response = requests.get(
			url,
			headers={"Authorization": "Bearer " + session["access_token"]},
		)
		data = response.json()
		image = data['images'][0]['url']
		for track in data['tracks']['items']:
			tracks.append({
				'track_id': track.get('id'),
				'track_images': track.get('images', image),
				'track_number': track.get('track_number'),
				'track_title': track.get('name'),
				'track_duration': calculate_duration(track.get('duration_ms')),
				'track_url': track.get('external_urls')['spotify'],
				'track_artists':[i.get("name") for i in track.get('artists')],
				'track_file': find_file( os.path.join(os.getcwd(), "static", "music", 'track'), track['id']),
			})
		url = data.get('next')
	return tracks

# albums
@app.route("/album/<id>", methods=["GET", "POST"])
@require_valid_token
def album(id):
	url = f"https://api.spotify.com/v1/albums/{id}"
	response = requests.get(
		url = url,
		headers={"Authorization": "Bearer " + session["access_token"]},
	)
	jsonResponse = json.loads(response.content)
	tracks = get_tracks(url)
	return render_template("album.html", album=jsonResponse, tracks=tracks)



@app.route('/download_track')
def download_track():
	song = request.args.to_dict()  # Convert the query parameters to a dictionary
	# print(song)  # Print the song dictionary 
	confirm = True
	while confirm:
		confirm, track, file_path = track_download(song.get("track_url"))
		if audio_duration(file_path) < song.get('track_duration'):
			confirm = True
			return True 
		confirm = False
		break		
	track = url_for('static', filename=track)
	print(track)
	return {"message": "Success", "track_path": track}


@app.route('/save_track')
def save_track():
	song = request.args.to_dict()  # Convert the query parameters to a dictionary
	print(song)  # Print the song dictionary
	if track_download(song.get("track_url"),static=False):
		return {"message": "Success"}



# Run the app when the script is executed
# if __name__ == "__main__":
# 	app.jinja_env.auto_reload = True
# 	app.config["TEMPLATES_AUTO_RELOAD"] = True
# 	# download_file("https://share33.com/2023/Busta%20Rhymes%20-%20BLOCKBUSTA%20-%20(SongsLover.com).zip", "bigfile.zip")
# 	app.run(debug=True)
