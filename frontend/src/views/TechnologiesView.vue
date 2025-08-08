<template>
  <div class="TechnologiesView">
    <h2>{{ t('SidebarButton.Technologies') }}</h2>
    <p>{{ t('technologies.description') }}</p>
    <InteractiveMap />
  </div>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import InteractiveMap from '@components/InteractiveMap.vue'
const { t } = useI18n()
</script>
<style scoped>
.TechnologiesView {
  display: flex;
  flex-direction: column;
}
.TechnologiesView h2 {
  margin: 0;
}
.TechnologiesView p {
  margin: 5px 0 5px 0;
}
</style>
