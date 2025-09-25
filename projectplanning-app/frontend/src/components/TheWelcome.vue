<template>
  <div class="welcome">
    <div class="simple-welcome">
      <h1>Bienvenido al portal de Project Planning.</h1>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.welcome {
  width: 100%;
  padding: 2rem;
}

.simple-welcome {
  text-align: center;
  padding: 4rem 2rem;
}

.simple-welcome h1 {
  font-size: 2.5rem;
  color: #333;
  font-weight: 300;
  line-height: 1.4;
}

@media (max-width: 768px) {
  .simple-welcome h1 {
    font-size: 2rem;
  }

  .simple-welcome {
    padding: 2rem 1rem;
  }
}
</style>
