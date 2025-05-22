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
      <QuestionWaiting v-if="mode === 'waiting'" :count="waitingCount" />
      <QuestionDisplay v-else-if="mode === 'question'" :content="questionContent" />
    </template>
  </div>
</template>

<script lang="ts" src="./QuestionSection"></script>

<style scoped>
.notice {
  border-left: 4px solid #ccc;
  padding-left: 12px;
  color: #555;
  font-style: italic;
  background-color: #f9f9f9;
  margin: 12px 0;
}
</style>
