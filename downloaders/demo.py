
import concurrent.futures


def download_chunk(DL_LINK, filepath):
    try:
        link = self.session.get(DL_LINK, stream=True)
        total_size = int(link.headers.get('content-length', 0))
        block_size = 1024  # 1 Kilobyte
        downloaded = 0

        with open(filepath, "wb") as f:
            for data in link.iter_content(block_size):
                f.write(data)
                downloaded += len(data)

        # Verify if the downloaded size matches the expected total size
        if downloaded != total_size:
            print(f"Downloaded size ({downloaded} bytes) does not match expected total size ({total_size} bytes). Re-downloading...")
            return self.download_chunk(DL_LINK, filepath)  # Recursive re-download

        print("Saved", os.path.basename(filepath))
        return True
    except Exception as e:
        print(f"Error downloading chunk: {e}")
        return False

def download_song(self, DL_LINK, filepath):
    try:
        link = self.session.get(DL_LINK, stream=True)
        total_size = int(link.headers.get('content-length', 0))
        block_size = 1024  # 1 Kilobyte
        downloaded = 0

        with open(filepath, "wb") as f:
            for data in link.iter_content(block_size):
                f.write(data)
                downloaded += len(data)

        print("Saved", os.path.basename(filepath))
        return True
    except Exception as e:
        print(f"Error downloading song: {e}")
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
