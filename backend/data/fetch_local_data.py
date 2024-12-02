import asyncio
import pymysql
from pycloudmusic import Music163Api
from flask import jsonify
import time

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "cloudmusic",
    "charset": "utf8mb4"
}

def fetch_data_as_dictlist(query, params=None):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchall()  # 获取查询结果
            return result  # 返回结果集（字典列表）
    finally:
        connection.close()

def fetch_data_as_dict(query, params=None):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()  # 获取一个结果
            return result  # 返回结果
    finally:
        connection.close()

def user_info(user_id):
    query = "SELECT * FROM users WHERE user_id = %s"
    user_info = fetch_data_as_dict(query, (user_id, ))
    print(user_info)
    return jsonify(user_info)

def user_playlists(user_id):
    query = """
                    SELECT playlist_id
                    FROM user_playlist
                    WHERE user_id = %s
                """
    playlist_ids = fetch_data_as_dictlist(query, (user_id, ))
    if not playlist_ids:
        return jsonify({'playlists': []})

    # 提取 playlist_id 列表
    playlist_id_list = [str(row["playlist_id"]) for row in playlist_ids]

    # 动态生成 SQL 查询
    placeholders = ", ".join(["%s"] * len(playlist_id_list))
    playlists_query = f"""
        SELECT * 
        FROM playlists
        WHERE playlist_id IN ({placeholders})
    """
    # 查询 playlists 表并返回结果
    playlists = fetch_data_as_dictlist(playlists_query, playlist_id_list)
    return jsonify({'playlists': playlists})

def songs_in_playlist(playlist_id):
    songs_query = "SELECT song_id FROM playlist_songs WHERE playlist_id = %s"
    playlist_songs = fetch_data_as_dictlist(songs_query, (playlist_id,))
    if not playlist_songs:
        return jsonify({'musics': []})

    song_id_list = [str(row["song_id"]) for row in playlist_songs]

    placeholders = ", ".join(["%s"] * len(song_id_list))
    songs_in_playlist_query = f"SELECT * FROM songs WHERE song_id IN ({placeholders})"

    songs = fetch_data_as_dictlist(songs_in_playlist_query, song_id_list)
    return jsonify({'musics': songs})

def song_if_downloaded(song_id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            query = "SELECT downloaded FROM songs WHERE song_id = %s"
            cursor.execute(query,(song_id, ))
            result = cursor.fetchone()
            print(result)
            if result:
                return bool(result[0])  # 确保返回布尔类型
            else:
                return False  # 歌曲不存在
    finally:
        connection.close()

def song_set_downloaded(song_id,status):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cursor:
            query = "UPDATE songs SET downloaded = %s WHERE song_id = %s"
            affected_rows = cursor.execute(query, (int(status), song_id))
            connection.commit()
            print("歌曲已标记")
            return affected_rows > 0
    except Exception as e:
        print(f"error:{e}")
        return False
    finally:
        connection.close()

def get_song_filename(song_id,level):
    connection = pymysql.connect(**db_config)
    query = "SELECT name,artist_name FROM songs WHERE song_id = %s"
    song_name = fetch_data_as_dict(query, (song_id, ))
    if level == 1:
        filename = f"{song_name['name']} - {song_name['artist_name']}.mp3"
    elif level == 2:
        filename = f"{song_name['name']} - {song_name['artist_name']}.flac"
    return filename

if __name__ == "__main__":
    get_song_filename()



