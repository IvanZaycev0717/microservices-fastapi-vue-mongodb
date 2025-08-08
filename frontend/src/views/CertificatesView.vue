<template>
  <div class="CertificatesView">
    <h2>{{ t('SidebarButton.Certificates') }}</h2>
    <p>{{ t('CertificatesView.description') }}</p>
    <CerfsGallery />
  </div>
</template>
<script setup>
import CerfsGallery from '@components/CerfsGallery.vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>
<style scoped>
.CertificatesView {
  overflow-y: auto;
}

.CertificatesView h2 {
  margin: 0;
}
.CertificatesView p {
  margin: 5px 0 5px 0;
  padding-right: 5px;
}
</style>
