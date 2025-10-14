<template>
  <div class="gallery-container">
    <div class="thumbnails">
      <img
        v-for="(img, idx) in sortedImages"
        :key="img.src"
        :src="img.thumb"
        @click="showLightbox(img.src)"
        class="thumbnail"
        :alt="img.alt"
      />
    </div>

    <vue-easy-lightbox
      :visible="visible"
      :imgs="sortedImages"
      :index="currentIndex"
      @hide="handleHide"
    />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import { useSortStore } from '@stores/sortStore.js'
import axios from 'axios'

const sortStore = useSortStore()

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
})

const visible = ref(false)
const currentIndex = ref(0)
const images = ref([])
const loading = ref(false)

const fetchCertificates = async (sortOption) => {
  try {
    loading.value = true
    const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_CERTIFICATES, {
      params: { sort: sortOption }
    })
    images.value = response.data.certificates
  } catch (err) {
    console.error('Ошибка загрузки сертификатов:', err)
  } finally {
    loading.value = false
  }
}

const showLightbox = (imgSrc) => {
  currentIndex.value = images.value.findIndex((img) => img.src === imgSrc)
  visible.value = true
}

const handleHide = () => {
  visible.value = false
}

const sortedImages = computed(() => images.value)

onMounted(() => {
  fetchCertificates(sortStore.selectedOption)
})


watch(() => sortStore.selectedOption, (newSort) => {
  fetchCertificates(newSort)
})
</script>

<style scoped>
.gallery-container {
  width: 100%;
  margin: 0 auto;
}

.thumbnails {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.thumbnail {
  width: 100%;
  height: 150px;
  object-fit: cover;
  cursor: pointer;
  transition: transform 0.2s;
  border-radius: 4px;
}

.thumbnail:hover {
  transform: scale(1.03);
}
</style>
