<template>
  <div class="interview-container">
    <div class="hints-container">
      <h2>第 {{ currentQuestion + 1 }} 题</h2>
      <p>{{ content }}</p>
    </div>
    <div class="buttons">
      <div class="feedback-section">
        <div class="feedback-container">
          <span class="label">你的打分：</span>
          <div class="feedback-container">
            <button v-for="rate in 5" :key="rate" :class="['rate-button', { selected: selectedRate === rate }]"
              @click="onRateClick(rate)">
              {{ rate }}
            </button>
          </div>
          <div class="button-container">
            <button class="blue-button" :disabled="currentQuestion === 0" @click="onLastQuestionClick"> &lt; </button>
            <button class="blue-button" @click="onNextQuestionClick">&gt;</button>
          </div>
        </div>
        <div class="feedback-container">
          <span class="label">注释：</span>
          <input class="comment-input" v-model="selectedcomment" />
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue';
import { getSocket } from '@/socket'

const socket = getSocket();

const props = defineProps<{
  content: string,
  currentQuestion: number,
  rating: number | null,
  comment: string
}>()

// const emit = defineEmits<{
//   (e: 'update:rating', value: number | null): void,
//   (e: 'update:comment', value: string): void,
// }>()

const selectedRate = ref<number | null>(props.rating);
const selectedcomment = ref<string>(props.comment)

// watch(() => props.rating, (newVal) => {
//   selectedRate.value = newVal;
// });
// watch(() => props.comment, (newVal) => {
//   selectedcomment.value = newVal;
// });

function onLastQuestionClick() {
  socket.send(JSON.stringify({ type: 'last', rating: selectedRate.value, comment: selectedcomment.value }))
}

function onNextQuestionClick() {
  if (selectedRate.value === null) {
    alert("请先为当前题目进行评分。");
    return;
  }
  socket.send(JSON.stringify({ type: 'next', rating: selectedRate.value, comment: selectedcomment.value }))
}

function onRateClick(rate: number) {
  selectedRate.value = rate;
}
</script>


<style scoped>
.interview-container {
  position: flex;
  flex-direction: column;
  overflow: hidden;
}

.hints-container {
  flex: 1;
  overflow-y: auto;
}


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

.blue-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  filter: none;
}

.rate-button {
  background-color: #ccc;
}

.rate-button.selected {
  background-color: var(--ez-blue);
}

.button-container {
  display: flex;
  justify-content: flex-end;
  gap: 0.8em;
}

.rank-container {
  display: flex;
  gap: 0.8em;
}

.feedback-section {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-top: 1.5em;
  gap: 1em;
}

.feedback-container {
  display: flex;
  align-items: center;
  gap: 0.8em;
  width: 100%;
}

.label {
  min-width: 5em;
}

.comment-input {
  flex: 1;
  min-width: 200px;
  padding: 0.5em 0.8em;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.95em;
  outline: none;
  transition: border-color 0.2s ease;
}

.comment-input:focus {
  border-color: var(--ez-blue);
}
</style>
