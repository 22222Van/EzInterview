<template>
  <div>
    <h2>题目</h2>
    <p>{{ content }}</p>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ content: string }>()
</script>
