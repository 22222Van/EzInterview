<template>
  <div>
    <p>面试将在 {{ countdown }} 秒后开始。祝你一切顺利！</p>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ countdown: number }>()
</script>
