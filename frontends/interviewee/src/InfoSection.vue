<template>
  <div class="info-section">
    <img :src="avatarUrl" alt="头像" class="avatar" />
    <div class="info">
      <p><strong>姓名：</strong>{{ student.name }}</p>
      <p><strong>学号：</strong>{{ student.id }}</p>
    </div>
    <div class="controls-container">
      <div class="control-item">
        <label>音量</label>
        <span>{{ volume }}%</span>
        <input type="range" v-model="volume" min="0" max="100" />
      </div>
      <div class="control-item">
        <label>麦克风</label>
        <span>{{ micLevel }}%</span>
        <input type="range" v-model="micLevel" min="0" max="100" />
      </div>
      <div class="control-item">
        <label>网络质量</label>
        <span>{{ networkQuality }}</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" src="./InfoSection"></script>

<style scoped>
.info-section {
  flex: 1;
  background-color: #007bff;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid white;
  margin-bottom: 20px;
  object-fit: cover;
}

.info p {
  font-size: 18px;
  margin: 8px 0;
}

.controls-container {
  width: 100%;
  display: flex;
  gap: 15px;
  margin-top: 30px;
  padding: 0 10px;
}

.control-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.control-item label {
  font-size: 14px;
  margin-bottom: 8px;
}

.control-item input[type="range"] {
  width: 100%;
  margin: 5px 0;
  appearance: none;
  -webkit-appearance: none;
  height: 5px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  outline: none;
}

.control-item input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 16px;
  height: 16px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
}

.control-item span {
  font-size: 12px;
  margin-top: 5px;
  opacity: 0.9;
}
</style>
