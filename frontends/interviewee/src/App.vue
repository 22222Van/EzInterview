<template>
  <div class="container">
    <!-- 左侧题目区域 -->
    <div class="question-section">
      <h2>题目一</h2>
      <p>请简要分析人工智能对未来社会的影响，并结合实例说明你的观点。</p>
      <textarea v-model="answer" placeholder="请输入你的答案..."></textarea>
    </div>

    <!-- 右侧考生信息区域 -->
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
          <!-- <input type="range" v-model="networkQuality" min="0" max="100" /> -->
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" src="./App.ts"></script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}

.question-section {
  flex: 2;
  padding: 30px;
  overflow-y: auto;
}

.question-section h2 {
  font-size: 24px;
  margin-bottom: 10px;
}

.question-section p {
  font-size: 16px;
  margin-bottom: 20px;
}

.question-section textarea {
  width: 100%;
  height: 300px;
  padding: 10px;
  font-size: 16px;
  resize: vertical;
  border-radius: 4px;
}

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
