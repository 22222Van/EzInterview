<template>
  <div class="info-section">
    <div class="questions-selector">
      <div v-for="(question, index) in questionMains" :key="index" class="question-item"
        :class="{ 'disabled-item': index === realCurrentQuestion }">
        <label>
          <input type="checkbox" :value="index" v-model="availableQuestions" @change="sendChange"
            :disabled="index === realCurrentQuestion" />
          {{ question }}
        </label>
      </div>
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
  background-color: var(--ez-blue);
  color: white;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}

/* 1. 将 questions-selector 区域整体左对齐，并与父容器区分开来 */
.questions-selector {
  /* 占满宽度，并向左对齐 */
  width: 100%;
  align-self: flex-start;
  padding: 0 10px;
  /* 与 controls-container 统一的左右内边距 */
  box-sizing: border-box;
}

/* 2. 统一 question-item 的风格：背景、边框、间距等 */
.question-item {
  display: flex;
  align-items: center;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 4px;
  padding: 8px 12px;
  margin-bottom: 10px;
  transition: background 0.2s ease;
}

/* 鼠标移入时的高亮效果 */
.question-item:hover {
  background: rgba(255, 255, 255, 0.15);
}

/* 给 label 和文字添加一致的字体和配色 */
.question-item label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
  color: white;
  width: 100%;
}

/* 3. 自定义复选框样式，让其与整体风格保持一致 */
.question-item input[type='checkbox'] {
  /* 隐藏原生复选框 */
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.8);
  border-radius: 3px;
  margin-right: 8px;
  position: relative;
  cursor: pointer;
  outline: none;
  transition: background 0.2s ease, border-color 0.2s ease;
}

/* 选中态的表现：白色实心背景＋对比边框 */
.question-item input[type='checkbox']:checked {
  background: white;
  border-color: white;
}

/* 在选中态时显示对勾符号 */
.question-item input[type='checkbox']:checked::after {
  content: '';
  position: absolute;
  top: 2px;
  left: 5px;
  width: 4px;
  height: 8px;
  border: solid var(--ez-blue);
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* 4. 控制文字部分：保证与 controls-container 中的文字风格一致 */
.question-item label span,
.question-item label {
  font-size: 14px;
  color: white;
}

/* 保证 .questions-selector 和 .controls-container 的整体间距协调 */
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

.control-item input[type='range'] {
  width: 100%;
  margin: 5px 0;
  appearance: none;
  -webkit-appearance: none;
  height: 5px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 5px;
  outline: none;
}

.control-item input[type='range']::-webkit-slider-thumb {
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


/* —— 以下为新增，用于高亮 disabled 情况 —— */

/* 当 question-item 带有 .disabled-item 类时，整行白底，文字和边框都改为蓝色 */
.question-item.disabled-item {
  background: white !important;
  border-color: var(--ez-blue) !important;
  cursor: default;
  /* 禁用时不需要 hover 手型 */
}

/* 禁用态下去掉 hover 效果 */
.question-item.disabled-item:hover {
  background: white !important;
}

/* 控制 label 里的文字和复选框在禁用态下都变为蓝色 */
.question-item.disabled-item label {
  color: var(--ez-blue) !important;
  cursor: default;
  font-weight: bold; /* 让文字变粗 */
}

/* disabled 的 checkbox 边框和勾都改成蓝色 */
.question-item.disabled-item input[type='checkbox'] {
  border-color: var(--ez-blue);
  background: rgba(0, 0, 0, 0);
  /* 保持空白 */
  cursor: default;
}

/* 如果 disabled 且被选中，则勾勾也显示蓝色 */
.question-item.disabled-item input[type='checkbox']:checked {
  background: var(--ez-blue);
  border-color: var(--ez-blue);
}

.question-item.disabled-item input[type='checkbox']:checked::after {
  border-color: white;
  /* 白色对比勾 */
}
</style>
