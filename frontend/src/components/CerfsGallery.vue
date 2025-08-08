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
import { ref, computed } from 'vue'
import VueEasyLightbox from 'vue-easy-lightbox'
import { useSortStore } from '@stores/sortStore.js'

const sortStore = useSortStore()

const visible = ref(false)
const currentIndex = ref(0)

const images = ref([
  {
    src: 'MinDigitalCom_ALGOR',
    thumb: 'MinDigitalCom_ALGORThumb',
    date: new Date(2025, 6, 13),
    popularity: 85,
    alt: 'MinDigitalCom_ALGOR',
  },
  {
    src: 'MinDigitalCom_API',
    thumb: 'MinDigitalCom_APIThumb',
    date: new Date(2025, 5, 29),
    popularity: 80,
    alt: 'MinDigitalCom_API',
  },
  {
    src: 'MinDigitalCom_CSS',
    thumb: 'MinDigitalCom_CSSThumb',
    date: new Date(2025, 5, 29),
    popularity: 85,
    alt: 'MinDigitalCom_CSS',
  },
  {
    src: 'MinDigitalCom_Docker',
    thumb: 'MinDigitalCom_DockerThumb',
    date: new Date(2025, 6, 11),
    popularity: 75,
    alt: 'MinDigitalCom_Docker',
  },
])

const showLightbox = (imgSrc) => {
  currentIndex.value = sortedImages.value.findIndex((img) => img.src === imgSrc)
  visible.value = true
}

const handleHide = () => {
  visible.value = false
}

function sortImages(sortOption) {
  switch (sortOption) {
    case 'date_desc':
      return [...images.value].sort((a, b) => b.date - a.date)
    case 'date_asc':
      return [...images.value].sort((a, b) => a.date - b.date)
    case 'popular':
      return [...images.value].sort((a, b) => b.popularity - a.popularity)
    default:
      return images.value
  }
}

const sortedImages = computed(() => sortImages(sortStore.selectedOption))
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
