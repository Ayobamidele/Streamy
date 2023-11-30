import os
import requests
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def download_file(url, path):
    response = requests.get(url, stream=True)
    total = int(response.headers.get('content-length', 0))
    with open(path, 'wb') as file, tqdm(
            desc=path,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
        for data in response.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

urls = ['https://b-g-eu-9.feetcdn.com:2223/v3-hls-playback/6c19c036ce98a14c487842ca567be82c31e8f65a6ad38bb8ec2eb84af51d0078b8f9a276420d45222d04c79b56d2c3812825fca516905028ad9cf39d9dffcdb72dde81f523f7ed29c44c0a85a2092568d0ef2b43a7d75e8a7a88da0279ed51aca2db215f02995f48ef3d981f77ff5a5ad56ccafb1dfbbf337b830fd20c89c9b0aa314f92a133a0051e2b91e92db386e83146981564748058c7807272334383c60ad9216ebfee1edfcb1d9e3db2ac29ee/720/index.m3u8']  # replace with your URLs
path = "/path/to/save/files"  # replace with your path
music_folder = os.path.join(os.getcwd(), "music")

with ThreadPoolExecutor(max_workers=5) as executor:
    for url in urls:
        executor.submit(download_file, url, os.path.join(os.getcwd(),"movie"))
