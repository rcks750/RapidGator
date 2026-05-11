from pathlib import Path
import re
import sys
import time

import requests
from lxml import html

RPGURL_LOGIN = "https://rapidgator.net/api/v2/user/login"
RPGURL_FILEDOWNLOAD = "https://rapidgator.net/api/v2/file/download/"
RPG_XPATH_FILENAME = "//div[@class='text-block file-descr']//p//a//text()"
CHUNK_SIZE = 1024 * 1024


def sanitize_filename(name: str) -> str:
    name = name.strip().replace("\n", " ").replace("\r", " ")
    name = re.sub(r'[\\/*?:"<>|]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name or 'rapidgator_download'


def extract_file_id(url: str) -> str:
    parts = [p for p in url.strip('/').split('/') if p]
    if not parts:
        raise ValueError('Invalid Rapidgator URL.')
    if 'file' in parts:
        idx = parts.index('file')
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return parts[-1].replace('.html', '')


def get_original_filename(file_url: str, fallback: str) -> str:
    page = requests.get(file_url, timeout=30)
    page.raise_for_status()
    root = html.fromstring(page.text)
    result = root.xpath(RPG_XPATH_FILENAME)
    file_name = ''.join(word.strip() for word in result)
    return sanitize_filename(file_name or fallback)


def format_bytes(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024 or unit == 'TB':
            return f'{size:.2f} {unit}'
        size /= 1024


def print_progress(downloaded: int, total: int | None, started_at: float) -> None:
    elapsed = max(time.time() - started_at, 0.001)
    speed = downloaded / elapsed
    if total and total > 0:
        percent = (downloaded / total) * 100
        msg = f'\rDownloaded: {percent:6.2f}% | {format_bytes(downloaded)} / {format_bytes(total)} | {format_bytes(int(speed))}/s'
    else:
        msg = f'\rDownloaded: {format_bytes(downloaded)} | {format_bytes(int(speed))}/s'
    print(msg, end='', flush=True)


def main() -> int:
    if len(sys.argv) != 5:
        print('Usage: python rgcolab.py <EMAIL> <PASSWORD> <RAPIDGATOR_URL> <OUTPUT_DIR>')
        return 1

    username = sys.argv[1]
    password = sys.argv[2]
    rapidurl = sys.argv[3].strip()
    output_dir = Path(sys.argv[4]).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    login_response = requests.get(RPGURL_LOGIN, params={'login': username, 'password': password}, timeout=30)
    login_response.raise_for_status()
    login_data = login_response.json()
    if login_data.get('status') != 200 or 'response' not in login_data or 'token' not in login_data['response']:
        raise RuntimeError(f'Rapidgator login failed: {login_data}')

    token = login_data['response']['token']
    file_id = extract_file_id(rapidurl)
    file_name = get_original_filename(rapidurl, file_id)

    download_response = requests.get(RPGURL_FILEDOWNLOAD, params={'file_id': file_id, 'token': token}, timeout=30)
    download_response.raise_for_status()
    download_data = download_response.json()
    if download_data.get('status') != 200 or 'response' not in download_data or 'download_url' not in download_data['response']:
        raise RuntimeError(f'Rapidgator download link request failed: {download_data}')

    download_url = download_data['response']['download_url']
    destination = output_dir / file_name
    print(f'Downloading to: {destination}')

    with requests.get(download_url, stream=True, timeout=60) as response:
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0)) or None
        print(f'Total size: {format_bytes(total_size)}' if total_size else 'Total size: unknown')
        downloaded = 0
        started_at = time.time()
        with open(destination, 'wb') as fh:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if not chunk:
                    continue
                fh.write(chunk)
                downloaded += len(chunk)
                print_progress(downloaded, total_size, started_at)

    print()
    print(f'Completed: {destination}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
