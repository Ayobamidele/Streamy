import requests
import os
import json
import re



class FileBin:
	def __init__(self, file_path):
		self.file_path = file_path
		self.file_name = os.path.basename(file_path)
		self.bin = '09cefunin2hpufcs'
		self.file_size = str(os.path.getsize(file_path))
		print(f"File size is {self.file_size} bytes")
		if not self.check_bin():
			self.get_bin()
 
	def check_bin(self):
		headers = {
			'accept': 'application/json',
		}

		response = requests.get(f'https://filebin.net/{self.bin}', headers=headers)
		return True if response.status_code == 200 else False
	 
	def get_bin(self):
		response = requests.get("https://filebin.net/")

		if response.status_code == 200:
			html_content = response.text

			# Use a regular expression to find all anchor tags with rel="nofollow"
			nofollow_links = re.findall(r'<a[^>]+rel="nofollow"[^>]*href=["\'](.*?)["\']', html_content)[0]
			bin = nofollow_links.split("/")[-1]
			self.bin = bin
			return bin
		else:
			print('Failed to retrieve content')
			return False	 
  
  	
	def upload(self):
		with open(self.file_path, 'rb') as f:
			# Set up the headers with the file name
			headers = {
				'Accept': '*/*',
				'Accept-Language': 'en-US,en;q=0.5',
				'Accept-Encoding': 'gzip, deflate, br, zstd',
				'Referer': 'https://filebin.net/',
				'bin': self.bin,
				'filename': self.file_name,
				'Content-Type': 'application/octet-stream',
				'Content-Length': self.file_size,
				'Origin': 'https://filebin.net',
				'Connection': 'keep-alive',
				'Sec-Fetch-Dest': 'empty',
				'Sec-Fetch-Mode': 'cors',
				'Sec-Fetch-Site': 'same-origin',
				'Priority': 'u=1',
				}
			
			# Send the POST request with the file in the body and filename in the header
			response = requests.post(f'https://filebin.net/{self.bin}/{self.file_name}', headers=headers, data=f)

			# Check if the request was successful
			if response.status_code == 201:
				print('File uploaded successfully')
				# Process response if needed
				print(json.dumps(response.json(), indent=4))
				return self.download()
			else:
				print('Failed to upload file', response.json(), response)



	def download(self):
		headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
		'Accept': '*/*',
		'Accept-Language': 'en-US,en;q=0.5',
		# 'Accept-Encoding': 'gzip, deflate, br, zstd',
		'Referer': 'https://filebin.net/',
		'Connection': 'keep-alive',
		# 'Cookie': 'verified=2024-05-24',
		'Sec-Fetch-Dest': 'empty',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Site': 'same-origin',
		'Priority': 'u=1',
		}

		response = requests.get(f'https://filebin.net/{self.bin}/{self.file_name}', headers=headers)
		if response.status_code == 200:
			return response.url

