<template>
  <div>
    <p>面试将在 {{ countdown }} 秒后开始，请做好准备。</p>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ countdown: number }>()
</script>
