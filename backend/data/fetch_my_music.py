import asyncio
import pymysql
from pycloudmusic import Music163Api

# MySQL 连接配置
db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "123456",
    "database": "cloudmusic",
    "charset": "utf8mb4"
}

api_for_all = Music163Api()
cycles = 0
# 数据库操作函数
def upsert_data(cursor, table, data, unique_key):
    global cycles
    if data is None or not isinstance(data, dict):
        raise ValueError("Data should be a non-None dictionary.")
    print(f"Data: {data}")
    keys = ", ".join(data.keys())
    values = ", ".join(["%s"] * len(data))
    update_fields = ", ".join([f"{key} = VALUES({key})" for key in data.keys()])

    sql = f"""
        INSERT INTO {table} ({keys})
        VALUES ({values})
        ON DUPLICATE KEY UPDATE {update_fields};
    """
    cursor.execute(sql, tuple(data.values()))

# 处理用户信息
async def handle_user(cursor, user):
    user_data = {
        "user_id": user.id,
        "name": user.name,
        "level": user.level,
        "cover": user.cover,
        "vip": user.vip,
        "like_playlist_id" : user.like_playlist_id,
        "login_ip": user.login_ip,
        "login_time": user.login_time,
        "login_time_str" : user.login_time_str
    }
    upsert_data(cursor, "users", user_data, unique_key="id")

# 处理歌曲
async def handle_song(cursor, song):
    global api_for_all
    song_artist = await api_for_all.artist(song.artist[0]["id"])
    await handle_artist(cursor, song_artist)
    await handle_album(cursor,await song.album())
    song_data = {
        "song_id": song.id,
        "mv_id": song.mv_id,
        "album_id": song.album_data["id"],
        "name": song.name[0],
        "artist_id": song.artist[0]["id"],
        "cover": song.album_data["picUrl"],
        "album_name" : song.album_str,
        "artist_name" : song.artist_str
    }
    upsert_data(cursor, "songs", song_data, unique_key="song_id")

# 处理专辑
async def handle_album(cursor, album):
    global api_for_all
    album_artist = await api_for_all.artist(album.artist["id"])
    await handle_artist(cursor, album_artist)
    album_data = {
        "album_id": album.id,
        "name": album.name,
        "sub_type": album.sub_type,
        "artist_id": album.artist["id"],
        "cover": album.cover,
        "size": album.size,
        "description": album.description,
        "comment_count": album.comment_count,
        "share_count": album.share_count,
        "liked_count": album.liked_count
    }
    upsert_data(cursor, "albums", album_data, unique_key="album_id")

# 处理歌手
async def handle_artist(cursor, artist):
    artist_data = {
        "artist_id": artist.id,
        "name": artist.name,
        "brief_desc": artist.brief_desc_str,
        "album_size": artist.album_size,
        "music_size": artist.music_size,
        "mv_size": artist.mv_size,
        "cover": artist.cover
    }
    upsert_data(cursor, "artists", artist_data, unique_key="artist_id")

# 处理歌单
async def handle_playlist(cursor, playlist, user_id):
    global cycles
    playlist_data = {
        "playlist_id": playlist.id,
        "name": playlist.name,
        "cover": playlist.cover,
        "user_id": user_id,
        # "tags_str" : playlist.tags_str,
        # "tags": playlist.tags,
        "description": playlist.description,
        "play_count": playlist.play_count,
        "subscribed_count": playlist.subscribed_count,
        "create_time": playlist.create_time
    }
    upsert_data(cursor, "playlists", playlist_data, unique_key="playlist_id")
    # 处理歌单内的歌曲
    for music in playlist:
        await handle_song(cursor, music)
        playlist_song_data = {
            "playlist_id": playlist.id,
            "song_id": music.id,
            "added_at": None  # 这里可以设置具体的添加时间
        }
        upsert_data(cursor, "playlist_songs", playlist_song_data, unique_key="id")

async def handle_user_playlist(cursor, user):
    global api_for_all,cycles
    # 抓取用户歌单
    user_playlists = await user.playlist()
    for playlist in user_playlists:
        current_list = await api_for_all.playlist(playlist.id)
        await handle_playlist(cursor, current_list, user.id)
        user_playlist_data = {
            "user_id": user.id,
            "playlist_id": playlist.id,
            "favorite_time" : None
        }
        cycles += 1
        if cycles == 1:
            await asyncio.sleep(2)
            cycles = 0
        upsert_data(cursor, "user_playlist", user_playlist_data, unique_key="user_id")


def clear_tables(cursor):
    try:
        # 要清空的表列表
        tables = ["playlists", "playlist_songs", "user_playlist"]

        # 遍历表列表并清空内容
        for table in tables:
            sql = f"DELETE FROM {table};"
            cursor.execute(sql)
            print(f"Table {table} has been cleared.")
    except Exception as e:
        print(f"Error while clearing tables: {e}")


# 主函数
async def main():
    musicapi = Music163Api(
        cookies=' MUSIC_R_T=1730942908812; MUSIC_A_T=1730942846625; MUSIC_SNS=; MUSIC_U=00AF81A668A21E97740E8BAB5EDFA03A397F76832206D8F7326CC7542C9C0B0EFFD3A6FDD3A06ECF27AA12A85603EAFBC371FDF7D648FE0D5CD8E6DD4F2643AD2C72106CFB85D6FD2707D76AB7456018FEA041B92EF1B61CAA883E5D41BA92E55DA956FE7262229068795D5DB29A342CE2E8FAED4F6C45F07DB1372C9460E86952C69F6A3ADCAE990DFF3F8A096963E5A2E354E1EF048991345295FC5DFD45DCFC1BE5548A80479E4067AEBA679DB28513A1B4A3966F6D66D855DF4B55C2BCD06F7EE0DAF114C107936FFF3888BE2D0FB4B5285FB2FD5CFF686939B479FB874B4C921B489697F073287930A8262CA5B6DABCF50C252819B36D1D127B163B75BF9B5976FE0076EC3D7FEA8EECACE9CC259C4ACFBD09D7C60C0E7C4835E348A587FF3FC723E2C40044F25EB5E6037BB047C1800B92A2D4076FCF090ED0DC5B0D57DF; __csrf=ac2fd99e04780954ab8c3235b7ff474a; '
    )
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()

    try:
        # 抓取用户数据
        user = await musicapi.my()
        await handle_user(cursor, user)
        clear_tables(cursor)
        await handle_user_playlist(cursor, user)
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
        print("ok!")


asyncio.run(main())
