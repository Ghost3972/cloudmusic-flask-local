<script setup>
import { ref,onMounted,reactive } from 'vue'
import Player from "@/components/player/Player.vue";
import axios from 'axios'

const updateAudioTime = (value) => {
  audio.value.currentTime = parseFloat(value);
};


const user = reactive({
  name : '',
  id:0,
  coverUrl:'',
  level:0
})

const playlists = ref([]);
const songs = ref([])
const isSongListVisible = ref(false)
const currentPlaylist = ref(null)
const uid = ref(12671571164)

// 播放器状态
const audio = ref(new Audio());
const currentSong = ref(null); // 当前播放歌曲
const isPlaying = ref(false);
const currentTime = ref(0); // 当前播放时间
const duration = ref(0); // 音乐总时长
const playlist = ref([]); // 播放列表
const currentSongIndex = ref(-1); // 当前歌曲在播放列表中的索引


// 播放歌曲
// 播放歌曲，并添加到播放列表
const playSong = async (song) => {
  //把播放列表替换成当前歌单的歌曲
  playlist.value = songs.value.map(s => ({ ...s, downloaded: s.downloaded })); // 创建一个副本避免数据直接修改

  // 找到当前歌曲在播放列表中的索引
  const currentIndex = playlist.value.findIndex(s => s.song_id === song.song_id);

  // 播放歌曲
  if (!song.downloaded) {
    await downloadSong(song);
  }
  currentSong.value = song;
  audio.value.src = `http://127.0.0.1:5000/api/download/file?mid=${song.song_id}`;
  audio.value.play();
  isPlaying.value = true;
  currentSongIndex.value = currentIndex; // 更新当前歌曲索引
};

// 监听播放进度
audio.value.addEventListener('timeupdate', () => {
  currentTime.value = audio.value.currentTime;
  duration.value = audio.value.duration;
});

// 暂停或播放
const togglePlay = () => {
  if (isPlaying.value) {
    audio.value.pause();
  } else {
    audio.value.play();
  }
  isPlaying.value = !isPlaying.value;
};

// 播放上一首
const playPrevious = () => {
  if (playlist.value.length === 0) return;
  currentSongIndex.value = (currentSongIndex.value - 1 + playlist.value.length) % playlist.value.length;
  playSong(playlist.value[currentSongIndex.value]);
};

// 播放下一首
const playNext = () => {
  if (playlist.value.length === 0) return;
  currentSongIndex.value = (currentSongIndex.value + 1) % playlist.value.length;
  playSong(playlist.value[currentSongIndex.value]);
};

// 下载歌曲
const downloadSong = async (song) => {
  song.isDownloading = true;

  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/download/music?mid=${song.song_id}`, {
      withCredentials: true,
    });

    if (response.data.success) {
      console.log("下载成功:", song.name);

      // 重新请求歌曲数据，确保最新状态
      const songResponse = await axios.get(`http://127.0.0.1:5000/api/download/musicstat?mid=${song.song_id}`, {
        withCredentials: true,
      });
      song.downloaded = songResponse.data.status;
    } else {
      console.error("下载失败:", response.data.message);
    }
  } catch (error) {
    console.error("下载时发生错误:", error);
  } finally {
    // 移除下载中状态
    song.isDownloading = false;
  }
};

const fetchSongs =  async (playlistId) => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/playlist?pid=${playlistId}`, {
      withCredentials:true,
    });

    songs.value = response.data.musics.map((song) => ({
      ...song,
      isDownloading: false, // 新增临时状态，用于前端显示“下载中”
    }));
    // songs.value = response.data.musics;
    currentPlaylist.value = playlists.value.find((playlist) => playlist.playlist_id === playlistId);
    isSongListVisible.value = true
  } catch (error) {

  }
}

const goBackToPlaylists = async () => {
  isSongListVisible.value = false;
  songs.value = [];
  currentPlaylist.value = null
}
const fetchPlaylists = async () => {
  try {
    const response = await axios.get(`http://127.0.0.1:5000/api/user/playlists?uid=${uid.value}`, {
      withCredentials: true,
    });
    playlists.value = response.data.playlists;
  } catch (error) {
    console.log('获取歌单失败',error)
  }
};
const getUserInfo = async () => {
  try{
    const response = await axios.get(`http://127.0.0.1:5000/api/user/info?uid=${uid.value}`,{
      withCredentials: true
    })
    user.name = response.data.name
    user.id = response.data.user_id
    user.coverUrl = response.data.cover
    user.level = response.data.level
    if(!user.level){
      user.level = 0
    }
  } catch (error) {
    console.log('登录失败',error)
  }
}



onMounted(() => {
  fetchPlaylists()
  getUserInfo()
})
</script>

<template>
  <div class="container">
    <aside class="sidebar">
      <h2>冈易地音乐</h2>
      <br>
      <div v-if="user.coverUrl" class="user-avatar">
        <img :src="user.coverUrl" alt="用户头像" class="avatar" />
      </div>

      <p>用户名：{{ user.name }}</p>
      <p>用户 ID: {{ user.id }}</p>
      <p>用户等级: {{ user.level }}</p>
    </aside>

    <main class="content">
      <div v-if="!isSongListVisible">
        <h2>歌单列表</h2>
        <br>
        <div v-if="playlists.length > 0">
          <div v-for="playlist in playlists" :key="playlist.playlist_id" class="playlist-item">
            <img :src="playlist.cover" alt="歌单封面" style="width: 70px; height: 70px; border-radius: 10px;" />

            <div class="playlist-info">
              <h3 @click="fetchSongs(playlist.playlist_id)">{{playlist.name}}</h3>
              <p v-if="playlist.description">{{ playlist.description }}</p>
              <p v-else>歌单没有描述</p>
            </div>

          </div>
        </div>
        <p v-else>正在加载歌单...</p>
      </div>

      <div v-if="isSongListVisible">
        <button @click="goBackToPlaylists" class="back-button">返回</button>
        <h2>{{currentPlaylist.name}}</h2>
        <div v-if="songs.length > 0">
          <div v-for="song in songs" :key="song.id" class="song-item">
            <img :src="song.cover" alt="歌曲封面" class="song-cover" />
            <div class="song-info">
              <h3 @click="playSong(song)">{{song.name}}</h3>
              <p>专辑: {{ song.album_name }}</p>
              <p>歌手: {{ song.artist_name }}</p>
            </div>

            <div class="song-actions">
            <!-- 未下载状态 -->
            <button
              v-if="!song.downloaded && !song.isDownloading"
              @click="downloadSong(song)"
              class="download-button">
              下载
            </button>
            <!-- 下载中状态 -->
            <span v-if="song.isDownloading">...</span>
            <!-- 已下载状态 -->
            <span v-else-if="song.downloaded" class="downloaded-check">✔</span>
          </div>

          </div>
        </div>
        <p v-else>正在加载歌曲...</p>
      </div>
    </main>

    <Player
      :currentSong="currentSong"
      :isPlaying="isPlaying"
      :currentTime="currentTime"
      :duration="duration"
      @update:currentTime="updateAudioTime"
      :playPrevious="playPrevious"
      :togglePlay="togglePlay"
      :playNext="playNext"
    />

  </div>
</template>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  width: 100vw;
}

.sidebar {
  width: 250px;
  height: 100vh;
  position: fixed;
  background-color: #F9F9F9;
  padding: 20px;  /* 内边距 */
  box-shadow: 2px 0 5px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.sidebar p{
  color: black;
}

.user-avatar .avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%; /* 圆形头像 */
  margin-bottom: 20px; /* 底部间距 */
  box-shadow: 0px 0px 5px black;
}

.content {
  flex: 1;
  width: 100%;
  padding: 20px;
  margin-left: 270px;
  margin-bottom: 80px;
}

.playlist-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.playlist-item img {
  margin-right: 15px;
  border-radius: 10px;
}

.playlist-info h3 {
  margin : 0;
  font-size: 18px;
  font-weight: bold;
}

.playlist-info p {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.song-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.song-cover {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  margin-right: 15px;
}

.song-info h3 {
  margin: 0;
  font-size: 16px;
  font-weight: bold;
}

.song-info p {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
}

.back-button {
  padding: 10px 20px;
  background-color: #778899;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin-bottom: 20px;
}

.back-button:hover {
  background-color: #708090;
}

.song-actions {
  margin-left: auto;
}

.download-button {
  padding: 5px 10px;
  background-color: #778899;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.download-button:hover {
  background-color: #708090;
}

.downloaded-check {
  color: green;
  font-size: 20px;
  font-weight: bold;
}

</style>
