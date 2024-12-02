from flask import Flask, request, jsonify ,redirect ,Response, send_file
from flask_cors import CORS
from .data.fetch_local_data import *
from .data.downdef import *
app = Flask(__name__)
CORS(app, supports_credentials=True)  # 支持跨域携带 Cookie
@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/api/user/info',methods=['GET'])
def get_user_info():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({"error": "uid is required!"}), 400
    info = user_info(user_id)
    return info

@app.route('/api/user/playlists',methods=['GET'])
def get_user_playlists():
    user_id = request.args.get('uid')
    if not user_id:
        return jsonify({"error": "uid is required!"}), 400
    playlists = user_playlists(user_id)
    return playlists


@app.route('/api/playlist',methods=['GET'])
def get_playlist():
    playlist_id = request.args.get('pid')
    if not playlist_id:
        return jsonify({"error": "pid is required!"}), 400
    songs = songs_in_playlist(playlist_id)
    return songs

@app.route('/api/download/music',methods=['GET'])
def download_music():
    music_id = request.args.get('mid')
    if not music_id:
        return jsonify({"error": "mid is required!"}), 400
    status = download_song(music_id)
    if status:
        return jsonify({"success": True,"message":"下载成功"}), 200
    else:
        return jsonify({"success": False,"message":"下载失败"}), 200

@app.route('/api/download/musicstat',methods=['GET'])
def if_music_downloaded():
    music_id = request.args.get('mid')
    if not music_id:
        return jsonify({"error": "mid is required!"}), 400
    status = song_if_downloaded(music_id)
    if status:
        return jsonify({"status":True})
    else:
        return jsonify({"status":False})

@app.route('/api/download/file')
def download_file():
    music_id = request.args.get('mid')
    if not music_id:
        return jsonify({"error": "mid is required!"}), 400
    filename = get_song_filename(music_id,1)
    file_path = f"/Users/lifutai/PycharmProjects/flask_cloudmusic_local/Downloaded_Songs/{filename}"
    try:
        return send_file(file_path,as_attachment=True)
    except Exception as e:
        return jsonify({"error":str(e)})

@app.route('/Song_V1', methods=['GET', 'POST'])
def Song_v1():
    if request.method == 'GET':
        song_ids = request.args.get('ids')
        url = request.args.get('url')
        level = request.args.get('level')
        type_ = request.args.get('type')
    else:
        song_ids = request.form.get('ids')
        url = request.form.get('url')
        level = request.form.get('level')
        type_ = request.form.get('type')

    if not song_ids and not url:
        return jsonify({'error': '必须提供 ids 或 url 参数'}), 400
    if level is None:
        return jsonify({'error': 'level参数为空'}), 400
    if type_ is None:
        return jsonify({'error': 'type参数为空'}), 400

    jsondata = song_ids if song_ids else url
    cookies = parse_cookie(read_cookie())
    urlv1 = url_v1(ids(jsondata),level,cookies)
    namev1 = name_v1(urlv1['data'][0]['id'])
    lyricv1 = lyric_v1(urlv1['data'][0]['id'],cookies)

    if urlv1['data'][0]['url'] is not None:
        if namev1['songs']:
           song_url = urlv1['data'][0]['url']
           song_name = namev1['songs'][0]['name']
           song_picUrl = namev1['songs'][0]['al']['picUrl']
           song_alname = namev1['songs'][0]['al']['name']
           artist_names = []
           for song in namev1['songs']:
               ar_list = song['ar']
               if len(ar_list) > 0:
                   artist_names.append('/'.join(ar['name'] for ar in ar_list))
               song_arname = ', '.join(artist_names)
    else:
       data = jsonify({"status": 400,'msg': '信息获取不完整！'}), 400
    if type_ == 'text':
       data = '歌曲名称：' + song_name + '<br>歌曲图片：' + song_picUrl  + '<br>歌手：' + song_arname + '<br>歌曲专辑：' + song_alname + '<br>歌曲音质：' + music_level1(urlv1['data'][0]['level']) + '<br>歌曲大小：' + size(urlv1['data'][0]['size']) + '<br>音乐地址：' + song_url
    elif  type_ == 'down':
       data = redirect(song_url)
    elif  type_ == 'json':
       data = {
           "status": 200,
           "name": song_name,
           "pic": song_picUrl,
           "ar_name": song_arname,
           "al_name": song_alname,
           "level":music_level1(urlv1['data'][0]['level']),
           "size": size(urlv1['data'][0]['size']),
           "url": song_url,
           "lyric": lyricv1['lrc']['lyric'],
           "tlyric": lyricv1['tlyric']['lyric']
        }
       json_data = json.dumps(data)
       data = Response(json_data, content_type='application/json')
    else:
        data = jsonify({"status": 400,'msg': '解析失败！请检查参数是否完整！'}), 400
    return data

