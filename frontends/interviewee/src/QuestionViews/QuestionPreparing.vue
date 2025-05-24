<template>
  <div class="interview-container">
    <p><strong>您好，欢迎使用 EzInterview 面试系统！</strong></p>
    <p>本次面试共包含 {{ questionCount }} 道题目。当您准备就绪后，请点击下方的"我准备好了"按钮开始。</p>
    <p>
      <template v-if="queueCount === 0">
        当前暂无候选人在您前面。点击按钮后，面试将在 15 秒内自动开始。
      </template>
      <template v-else-if="queueCount === 1">
        目前有 1 位候选人在您之前，他仍需完成 {{ queueQuestionCount }} 道题目。请稍候，您的面试即将开始。
      </template>
      <template v-else>
        当前有 {{ queueCount }} 位候选人在您前面。请耐心等待，您的面试很快就会开始。
      </template>
    </p>
    <p>等待期间，您可以使用下方文本框测试键盘输入，或点击"测试音频"按钮检查扬声器/耳机是否正常。如遇技术问题，请点击"帮助"按钮联系我们的支持团队。</p>
    <p>感谢您的耐心等待，祝您面试顺利！</p>
    <textarea placeholder="" class="test-textarea"></textarea>
    <div class="buttons">
      <div class="button-container">
        <button class="blue-button" :style="{ visibility: mode === 'preparing' ? 'visible' : 'hidden' }"
          @click="onReadyClick"> 我准备好了
        </button>
      </div>
      <div class="bottom-controls">
        <button class="blue-button" @click="onHelpClick">帮助</button>
        <div class="bottom-right">
          <button class="blue-button" @click="onTestAudioClick">测试音频</button>
          <button class="red-button" @click="onQuitClick">放弃</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { getSocket } from '@/socket'

defineProps<{
  questionCount: number,
  queueCount: number,
  queueQuestionCount: number,
  mode: 'preparing' | 'waiting'
}>()

function onReadyClick() {
  const confirmQuit = confirm('确定要开始面试吗？');
  if (confirmQuit) {
    const socket = getSocket();
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'ready' }));
    } else {
      console.error('WebSocket 未连接');
    }
  }
}

function onHelpClick() {
  window.location.href = 'https://github.com/22222Van/EzInterview'
}

function onTestAudioClick() {
  // TODO
}

function onQuitClick() {
  const confirmQuit = confirm('确定要放弃此次面试吗？');
  if (confirmQuit) {
    window.location.href = 'about:blank';
  }
}
</script>

<style scoped>
.interview-container {
  position: relative;
}

.test-textarea {
  width: 100%;
  height: 4lh;
  border: 1px solid #ccc;
  margin-bottom: 1em;
}

/* 通用按钮样式 */
.buttons button {
  padding: 0.5em 1em;
  font-size: 0.95em;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  color: white;
  transition: filter 0.2s ease;
}

.buttons button:hover {
  filter: brightness(0.9);
}

.blue-button {
  background-color: var(--ez-blue);
}

.red-button {
  background-color: var(--ez-red);
}

.button-container {
  text-align: left;
}

.bottom-controls {
  padding: 1em 0;
  display: flex;
  justify-content: space-between;
}

.bottom-right {
  display: flex;
  gap: 0.8em;
}
</style>
