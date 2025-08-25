<script setup>
import { onMounted, ref } from 'vue'
import 'vue3-carousel/carousel.css'
import axios from 'axios'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import AboutMeCard from '@components/AboutMeCard.vue'


const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT),
  headers: {
    'Content-Type': 'application/json',
  }
})

const cards = ref([])
const loading = ref(true)
const error = ref(null)
const isMounted = ref(false)

const fetchAboutData = async () => {
  try {
    loading.value = true
    error.value = null
    
    const response = await apiClient.get(import.meta.env.VITE_API_CONTENT_ABOUT)

    cards.value = response.data
    
  } catch (err) {
    if (err.response) {
      error.value = `Ошибка сервера: ${err.response.status} - ${err.response.data?.message || err.response.statusText}`
    } else if (err.request) {
      error.value = 'Не удалось подключиться к серверу. Проверьте соединение.'
    } else {
      error.value = `Ошибка при настройке запроса: ${err.message}`
    }
    console.error('Ошибка при загрузке данных:', err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  isMounted.value = true
  fetchAboutData()
})

const carouselConfig = {
  itemsToShow: 1,
  snapAlign: 'center',
  wrapAround: true,
  autoplay: 4000,
  mouseWheel: true,
  pauseAutoplayOnHover: true,
  transition: 600,
  gap: 5,
}
</script>

<template>
  <Carousel v-if="isMounted" v-bind="carouselConfig">
    <Slide v-for="(card, index) in cards" :key="index">
      <AboutMeCard>
        <template #image>
          <img
            fetchpriority="high"
            v-lazy="{
              src: card.image,
              loading: card.placeholder,
            }"
            :alt="card.title"
            class="card-image"
            width="800"
            height="600"
          />
        </template>

        <template #title>{{ card.title }}</template>
        <template #description>
          <p>{{ card.description }}</p>
        </template>
      </AboutMeCard>
    </Slide>

    <template #addons>
      <Navigation />
      <Pagination />
    </template>
  </Carousel>
</template>

<style scoped>
.carousel {
  height: 60vh;
  --vc-pgn-background-color: var(--text-color);
  --vc-pgn-active-color: var(--header-title-color);
}

.carousel__slide {
  padding: 10px;
  transition: all 0.3s ease;
  display: flex;
  justify-content: center;
}

:deep(.carousel__prev),
:deep(.carousel__next) {
  color: #4a6fa5;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  width: 40px;
  height: 40px;
}

:deep(.carousel__pagination) {
  margin-top: 20px;
}
.card-image {
  max-width: 100%;
  max-height: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  border-radius: 12px;
}

.card-image[lazy='loading'] {
  opacity: 0.6;
  background: transparent;
  filter: blur(2px);
}

.card-image[lazy='loaded'] {
  opacity: 1;
  transition: opacity 0.3s ease;
}
</style>
