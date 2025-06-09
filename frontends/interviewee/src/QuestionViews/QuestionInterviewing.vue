<template>
  <div>
    <p>请回答第 {{ currentQuestion + 1 }} 题。</p>
    <template v-if="hint && hint.trim() !== ''">
      <h3>提示</h3>
      <p>{{ hint }}</p>
    </template>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ currentQuestion: number, hint: string }>()
</script>
