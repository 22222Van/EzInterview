<template>
  <div class="question-section">
    <template v-if="connectionStatus === 'connecting'">
      <h2>连接中...</h2>
      <p>正在尝试连接到服务器，请稍候。</p>
    </template>

    <template v-else-if="connectionStatus === 'error'">
      <h2>连接失败</h2>
      <p>无法连接到服务器。请确认后端是否已经启动。</p>
      <blockquote class="notice">
        提示：你需要先启动后端再启动前端。你可以在重新启动后端后刷新网页重试。
      </blockquote>
    </template>

    <template v-else>
      <template v-if="mode === 'waiting'">
        <h2>请稍候</h2>
        <p>您当前排队中，前方还有 {{ waitingCount }} 人。</p>
        <textarea placeholder="" class="test-textarea"></textarea>
      </template>
      <template v-else-if="mode === 'question'">
        <h2>题目</h2>
        <p>{{ questionContent }}</p>
      </template>
    </template>
  </div>
</template>

<script lang="ts" src="./QuestionSection"></script>

<style scoped>
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
  white-space: pre-line;
}

.notice {
  border-left: 4px solid #ccc;
  padding-left: 12px;
  color: #555;
  font-style: italic;
  background-color: #f9f9f9;
  margin: 12px 0;
}

.test-textarea {
  width: 100%;
  height: 100px;
  margin-top: 15px;
  padding: 10px;
  font-size: 16px;
  resize: none;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
}
</style>
