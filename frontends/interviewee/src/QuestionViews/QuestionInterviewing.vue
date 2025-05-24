<template>
  <div>
    <p>请回答第 {{ currentQuestion + 1 }} 题。</p>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ currentQuestion: number }>()
</script>
