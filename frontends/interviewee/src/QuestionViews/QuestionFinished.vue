<template>
  <div class="interview-container">
    <p><strong>恭喜！您已完成本次面试！</strong></p>
    <div class="buttons">
      <div class="bottom-controls" style="justify-content: flex-start;">
        <button class="blue-button" @click="onHelpClick">关于 EzIntervew</button>
        <button class="blue-button" @click="onQuitClick">退出系统</button>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
function onHelpClick() {
  window.location.href = 'https://github.com/22222Van/EzInterview'
}

function onQuitClick() {
  window.location.href = 'about:blank';
}
</script>

<style scoped>
.interview-container {
  position: relative;
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

.bottom-controls {
  padding: 1em 0;
  display: flex;
  gap: 1em;
}

.bottom-right {
  display: flex;
  gap: 0.8em;
}
</style>
