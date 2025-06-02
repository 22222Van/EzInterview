<template>
  <div>
    <p>请回答第 {{ currentQuestion + 1 }} 题。</p>
    <h3>提示</h3>
    <p>{{ hint }}</p>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ currentQuestion: number, hint: string }>()
</script>
