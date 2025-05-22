<template>
  <div>
    <h2>请稍候</h2>
    <p>您当前排队中，前方还有 {{ count }} 人。</p>
    <textarea placeholder="" class="test-textarea"></textarea>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ count: number }>()
</script>

<style scoped>
.test-textarea {
  width: 100%;
  height: 200px;
  border: 1px solid #ccc;
}
</style>
