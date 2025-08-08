<template>
  <div class="ProjectsView">
    <h2>{{ t('ProjectsView.title') }}</h2>
    <p>{{ t('ProjectsView.description') }}</p>
    <ProjectPortfolio />
  </div>
</template>
<script setup>
import { useI18n } from 'vue-i18n'
import ProjectPortfolio from '@components/ProjectPortfolio.vue'
const { t } = useI18n()
</script>
<style scoped>
.ProjectsView {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.ProjectsView h2 {
  margin: 0;
}
.ProjectsView p {
  margin: 5px 0 5px 0;
}
</style>
