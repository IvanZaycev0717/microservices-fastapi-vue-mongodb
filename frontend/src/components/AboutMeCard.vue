<template>
  <div class="card">
    <div class="image-container">
      <slot name="image"></slot>
    </div>
    <div class="content">
      <h3 class="title">
        <slot name="title"></slot>
      </h3>
      <div class="description">
        <slot name="description"></slot>
      </div>
    </div>
  </div>
</template>

<script setup></script>

<style scoped>
.card {
  display: flex;
  width: 85%;
  max-width: 95%;
  height: 85%;
  background-color: var(--hover-button-background-color);
  border: 2px solid var(--text-color);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.image-container {
  width: 40%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: inherit;
  padding: 10px;
  box-sizing: border-box;
}

.image-container:hover img {
  transform: scale(1.05);
}

.content {
  width: 60%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.title {
  margin: 0 0 12px 0;
  font-size: 1.2rem;
  font-weight: 600;
  color: var(--text-color);
  text-align: left;
}

.description {
  margin: 0;
  font-size: 0.9rem;
  color: var(--text-color);
  text-align: left;
}

@media (max-width: 480px) {
  .card {
    flex-direction: column;
    height: auto;
  }

  .image-container {
    width: 100%;
    height: 160px;
  }

  .content {
    width: 100%;
    padding: 16px;
    text-align: center;
  }
}

@media (min-width: 1920px) {
  .title {
    font-size: 1.85rem;
    font-weight: 600;
    color: var(--text-color);
  }

  .description {
    margin: 0;
    font-size: 1.7rem;
    line-height: 1.5;
    color: var(--text-color);
  }
}
</style>
