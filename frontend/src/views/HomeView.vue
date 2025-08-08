<template>
  <div class="HomeView">
    <div class="author">
      <div class="avatar-container">
        <img src="@assets/photo/my_photo.webp" alt="my_photo" class="avatar" />
      </div>
      <h1>{{ t('author') }}</h1>
      <div class="title">
        <span>{{ t('desc1') }}</span>
        <span class="separator"> | </span>
        <span>{{ t('desc2') }}</span>
        <span class="separator"> | </span>
        <span>{{ t('desc3') }}</span>
      </div>
      <div class="social__container">
        <GitHubIcon />
        <TelegramIcon />
        <LeetCodeIcon />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

import GitHubIcon from '@icons/GitHubIcon.vue'
import TelegramIcon from '@icons/TelegramIcon.vue'
import LeetCodeIcon from '@icons/LeetCodeIcon.vue'
</script>

<style scoped>
.HomeView {
  margin: 0 auto;
  overflow-y: auto;
  width: 100%;
}

.author {
  margin-bottom: 2rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar {
  border-radius: 50%;

  object-fit: cover;
  border: 3px solid var(--selection-color);
  filter: grayscale(100%);
  transition:
    filter 0.5s ease,
    transform 0.3s ease;
}

.title {
  padding: 10px;
  font-size: 0.75rem;
}

@media (min-width: 2560px) {
  .avatar {
    width: 450px;
    height: 450px;
    border-width: 1.5px;
  }

  .title {
    font-size: 1.3rem;
  }
}

@media (max-width: 1920px) {
  .avatar {
    width: 350px;
    height: 350px;
    border-width: 1.5px;
  }

  .title {
    font-size: 1rem;
  }
}

@media (max-width: 1440px) {
  .avatar {
    width: 400px;
    height: 400px;
    border-width: 1.5px;
  }
}

@media (max-width: 1280px) {
  .avatar {
    width: 150px;
    height: 150px;
    border-width: 1.5px;
  }
  .title {
    font-size: 0.7rem;
  }
}

@media (max-width: 768px) {
  .avatar {
    width: 250px;
    height: 250px;
    border-width: 1.5px;
  }

  .title {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .separator {
    display: none;
  }
}

@media (max-width: 768px) {
  .title {
    display: flex;
    flex-direction: column;
  }
}

.avatar:hover {
  filter: grayscale(0%);
  transform: scale(1.05);
}

.avatar-container {
  display: inline-block;
}

.separator {
  margin: 0 0.5rem;
  color: #999;
}

h1 {
  font-size: 2rem;
  margin: 1rem 0 0.5rem;
}

.social__container {
  display: flex;
  width: 100%;
  justify-content: space-around;
  margin-top: 20px;
}
</style>
