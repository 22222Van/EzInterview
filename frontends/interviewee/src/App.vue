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

/* 左侧题目区域 */
.question-section {
  flex: 2;
  padding: 30px;
  overflow-y: auto;
  background-color: #f9f9f9;
  border-right: 1px solid #ccc;
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
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 右侧信息区域 */
.info-section {
  flex: 1;
  background-color: #007bff;
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
  /* width: 1000px; */
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
</style>
c:\Users\Dell\Downloads\新建文件夹\App.ts
