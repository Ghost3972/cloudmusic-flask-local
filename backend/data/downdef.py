import json
import os
import urllib.parse
from hashlib import md5
from random import randrange
import requests
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from .fetch_local_data import *

def download_song(song_id):
    # 定义下载接口
    url = f"http://127.0.0.1:5000/Song_V1?ids={song_id}&level=exhigh&type=json"

    try:
        if song_if_downloaded(song_id):
            print("歌曲之前已下载！")
            return 1
        # 获取歌曲信息
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200:
            print(f"下载失败：接口返回错误，状态码 {data.get('status')}")
            return 0

        # 提取歌曲信息
        song_name = data["name"]
        album_name = data["al_name"]
        artist_name = data["ar_name"]
        song_url = data["url"]
        cover_url = data["pic"]
        file_size = data["size"]

        # 确定保存路径和文件名
        song_filename = f"{song_name} - {artist_name}.mp3"
        cover_filename = f"{song_name} - {artist_name}.jpg"


        # 创建存储文件夹
        output_dir = "Downloaded_Songs"
        os.makedirs(output_dir, exist_ok=True)
        song_filepath = os.path.join(output_dir, song_filename)
        cover_filepath = os.path.join(output_dir, cover_filename)

        # 下载歌曲文件
        print(f"正在下载歌曲: {song_name} ({file_size})")
        song_response = requests.get(song_url, stream=True)
        with open(song_filepath, "wb") as song_file:
            for chunk in song_response.iter_content(chunk_size=1024):
                song_file.write(chunk)
        print(f"歌曲下载完成: {song_filepath}")

        # 下载专辑封面
        print(f"正在下载专辑封面: {cover_url}")
        cover_response = requests.get(cover_url, stream=True)
        with open(cover_filepath, "wb") as cover_file:
            for chunk in cover_response.iter_content(chunk_size=1024):
                cover_file.write(chunk)
        print(f"专辑封面下载完成: {cover_filepath}")

        # 写入标签信息
        print(f"正在为 {song_filename} 添加标签信息...")
        audio = EasyID3(song_filepath)
        audio["title"] = song_name
        audio["artist"] = artist_name
        audio["album"] = album_name
        audio.save()

        # 添加封面图片
        audio = ID3(song_filepath)
        with open(cover_filepath, "rb") as img:
            audio.add(APIC(
                mime="image/jpeg",  # 图片格式
                type=3,  # 封面类型
                desc="Cover",
                data=img.read()
            ))
        audio.save()
        print(f"标签信息添加完成！")

        # 删除临时下载的封面图片文件
        os.remove(cover_filepath)
        print(f"已删除临时封面文件: {cover_filepath}")
        song_set_downloaded(song_id,1)
        return 1

    except requests.exceptions.RequestException as e:
        print(f"下载过程中出现错误: {e}")
        return 0
    except KeyError as e:
        print(f"数据解析错误，缺少字段: {e}")
        return 0
    except Exception as e:
        print(f"处理标签时出现错误: {e}")
        return 0


def HexDigest(data):
    return "".join([hex(d)[2:].zfill(2) for d in data])


def HashDigest(text):
    HASH = md5(text.encode("utf-8"))
    return HASH.digest()


def HashHexDigest(text):
    return HexDigest(HashDigest(text))


def parse_cookie(text: str):
    cookie_ = [item.strip().split('=', 1) for item in text.strip().split(';') if item]
    cookie_ = {k.strip(): v.strip() for k, v in cookie_}
    return cookie_


def read_cookie():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookie_file = os.path.join(script_dir, 'cookie.txt')
    with open(cookie_file, 'r') as f:
        cookie_contents = f.read()
    return cookie_contents


def post(url, params, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154',
        'Referer': '',
    }
    cookies = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!"
    }
    cookies.update(cookie)
    response = requests.post(url, headers=headers, cookies=cookies, data={"params": params})
    return response.text


# 输入id选项
def ids(ids):
    if '163cn.tv' in ids:
        response = requests.get(ids, allow_redirects=False)
        ids = response.headers.get('Location')
    if 'music.163.com' in ids:
        index = ids.find('id=') + 3
        ids = ids[index:].split('&')[0]
    return ids


# 转换文件大小
def size(value):
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    size = 1024.0
    for i in range(len(units)):
        if (value / size) < 1:
            return "%.2f%s" % (value, units[i])
        value = value / size
    return value


# 转换音质
def music_level1(value):
    if value == 'standard':
        return "标准音质"
    elif value == 'exhigh':
        return "极高音质"
    elif value == 'lossless':
        return "无损音质"
    elif value == 'hires':
        return "Hires音质"
    elif value == 'sky':
        return "沉浸环绕声"
    elif value == 'jyeffect':
        return "高清环绕声"
    elif value == 'jymaster':
        return "超清母带"
    else:
        return "未知音质"


def url_v1(id, level, cookies):
    url = "https://interface3.music.163.com/eapi/song/enhance/player/url/v1"
    AES_KEY = b"e82ckenh8dichen8"
    config = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": "pyncm!",
        "requestId": str(randrange(20000000, 30000000))
    }

    payload = {
        'ids': [id],
        'level': level,
        'encodeType': 'flac',
        'header': json.dumps(config),
    }

    if level == 'sky':
        payload['immerseType'] = 'c51'

    url2 = urllib.parse.urlparse(url).path.replace("/eapi/", "/api/")
    digest = HashHexDigest(f"nobody{url2}use{json.dumps(payload)}md5forencrypt")
    params = f"{url2}-36cd479b6b5-{json.dumps(payload)}-36cd479b6b5-{digest}"
    padder = padding.PKCS7(algorithms.AES(AES_KEY).block_size).padder()
    padded_data = padder.update(params.encode()) + padder.finalize()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.ECB())
    encryptor = cipher.encryptor()
    enc = encryptor.update(padded_data) + encryptor.finalize()
    params = HexDigest(enc)
    response = post(url, params, cookies)
    return json.loads(response)


def name_v1(id):
    # 歌曲信息接口
    urls = "https://interface3.music.163.com/api/v3/song/detail"
    data = {'c': json.dumps([{"id": id, "v": 0}])}
    response = requests.post(url=urls, data=data)
    return response.json()


def lyric_v1(id, cookies):
    # 歌词接口
    url = "https://interface3.music.163.com/api/song/lyric"
    data = {'id': id, 'cp': 'false', 'tv': '0', 'lv': '0', 'rv': '0', 'kv': '0', 'yv': '0', 'ytv': '0', 'yrv': '0'}
    response = requests.post(url=url, data=data, cookies=cookies)
    return response.json()

