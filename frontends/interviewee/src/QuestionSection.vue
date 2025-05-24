<template>
  <div class="question-section">
    <div class="stepper-text">
      <span>Questions: </span>
      <span v-for="(step, index) in questionTitles" :key="index" :class="{
        past: index < currentQuestion,
        current: index === currentQuestion,
        future: index > currentQuestion
      }">
        {{ step }}
        <span v-if="index < questionTitles.length - 1"> > </span>
      </span>
    </div>

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
      <QuestionPreparing v-if="mode === 'preparing' || mode === 'waiting'" :queueCount="queueCount"
        :questionCount="questionCount" :queueQuestionCount="queueQuestionCount" :mode="mode" />
      <QuestionDisplay v-else-if="mode === 'interviewing'" :content="questionContent" />
      <QuestionCounting v-else-if="mode === 'counting'" :countdown="countdown" />
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

.stepper-text {
  font-size: 18px;
  margin-bottom: 16px;
}

.stepper-text span {
  font-weight: normal;
  color: #aaa;
}

.stepper-text .past {
  color: var(--ez-blue);
}

.stepper-text .current {
  font-weight: bold;
  color: var(--ez-green);
}

.stepper-text .future {
  color: #aaa;
}
</style>
