<template>
  <div class="AboutMeView">
    <h2>{{ t('SidebarButton.AboutMe') }}</h2>
    <AboutMeCarousel />
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
import AboutMeCarousel from '@components/AboutMeCarousel.vue'
</script>

<style scoped>
.AboutMeView {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.AboutMeView h2 {
  margin: 0 0 10px 0;
}
</style>
