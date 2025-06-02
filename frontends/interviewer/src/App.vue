<template>
  <div class="container">
    <QuestionSection />
    <InfoSection :availableQuestions="[1]" :questionMains="['114', '514']" />
  </div>
</template>

<script lang="ts" src="./App"></script>

<style scoped>
.container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}
</style>
