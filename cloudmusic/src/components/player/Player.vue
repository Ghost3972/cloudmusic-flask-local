<template>
  <footer class="player">
    <div v-if="currentSong" class="player-content">
      <div class="song-info">
        <img :src="currentSong.cover" alt="歌曲封面" class="song-cover">
        <div class="song-details">
          <h3>{{ currentSong.name }}</h3>
          <p>{{ currentSong.artist_name }} - {{ currentSong.album_name }}</p>
        </div>
      </div>
      <div class="player-controls">
        <button @click="playPrevious" class="mdc-button mdc-button--icon">
          <i class="material-icons">上一首</i>
        </button>
        <button @click="togglePlay" class="mdc-button mdc-button--icon" :class="{ 'mdc-button--raised': isPlaying }">
          <i class="material-icons">{{ isPlaying ? '暂停' : '继续播放' }}</i>
        </button>
        <button @click="playNext" class="mdc-button mdc-button--icon">
          <i class="material-icons">下一首</i>
        </button>
      </div>
        <div class="progress-bar">
          <input type="range" :value="currentTime" :max="duration" step="0.1" @input="$emit('update:currentTime', $event.target.value)">
          <span>{{ formatTime(currentTime) }} / {{ formatTime(duration) }}</span>
        </div>
    </div>
  </footer>
</template>

<script>
import { ref, computed } from 'vue';

export const formatTime = (seconds) => {
  if (isNaN(seconds)) {
    return '00:00';
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`;
};
export default {
  props: {
    currentSong: {
      type: Object,
      default: null,
    },
    isPlaying: {
      type: Boolean,
      default: false,
    },
    currentTime: {
      type: Number,
      default: 0,
    },
    duration: {
      type: Number,
      default: 0,
    },
    playPrevious: {
      type: Function,
      required: true,
    },
    togglePlay: {
      type: Function,
      required: true,
    },
    playNext: {
      type: Function,
      required: true,
    },
  },
  setup(props, context) {
    return {
        formatTime,
    };
  },
};
</script>

<style scoped>
.player {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: #fff;
  color: black;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0px -2px 5px rgba(0,0,0,0.1); /* 添加阴影 */
}

.player-content {
    display: flex;
    width: 80%;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
}

.song-info {
  display: flex;
  align-items: center;
}

.song-cover {
  width: 60px;
  height: 60px;
  border-radius: 5px;
  margin-right: 10px;
}

.song-details h3 {
  margin: 0;
  font-size: 16px;
}

.song-details p {
  margin: 5px 0 0 0;
  font-size: 14px;
  color: #777;
}

.player-controls {
  display: flex;
}

.mdc-button {
  margin: 0 10px;
}
.mdc-button--raised{
  background-color: #2196F3;
  color: white;
}

.progress-bar {
  display: flex;
  align-items: center;
  margin-left: 20px;
}

.progress-bar input[type="range"] {
  flex-grow: 1;
  width: 200px; /* 设置一个最小宽度，防止进度条太小 */
  -webkit-appearance: none; /* 隐藏默认样式 */
  appearance: none;
  background: #ddd;
  border-radius: 5px;
  outline: none;
}

.progress-bar input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 15px;
  height: 15px;
  background: slategrey;
  border-radius: 50%;
  cursor: pointer;
}

.progress-bar input[type="range"]::-moz-range-thumb {
  width: 15px;
  height: 15px;
  background: #2196F3;
  border-radius: 50%;
  cursor: pointer;
}

.progress-bar span {
  margin-left: 10px;
}
</style>
