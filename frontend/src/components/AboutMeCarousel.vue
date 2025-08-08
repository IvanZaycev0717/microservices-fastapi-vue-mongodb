<script setup>
import { onMounted, ref } from 'vue'
import 'vue3-carousel/carousel.css'
import { Carousel, Slide, Pagination, Navigation } from 'vue3-carousel'
import AboutMeCard from '@components/AboutMeCard.vue'

const cards = [
  { image: 'image_1.jpg', title: 'Some title 1', description: 'Some description 1' },
  { image: 'image_2.jpg', title: 'Some title 2', description: 'Some description 2' }
]

const isMounted = ref(false)
onMounted(() => {
  isMounted.value = true
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
    <Slide v-for="card in cards" :key="card.image">
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
