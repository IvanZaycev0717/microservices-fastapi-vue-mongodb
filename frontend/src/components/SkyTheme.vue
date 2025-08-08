<template>
  <div class="SkyTheme">
    <div class="day" :style="{ opacity: isDay ? 1 : 0 }"></div>
    <div class="night" :style="{ opacity: isDay ? 0 : 1 }"></div>

    <transition-group name="fade">
      <div v-if="isDay" class="cloud1" key="cloud1"></div>
      <div v-if="isDay" class="cloud2" key="cloud2"></div>
      <div v-if="isDay" class="cloud3" key="cloud3"></div>
      <div v-if="isDay" class="cloud4" key="cloud4"></div>
    </transition-group>
    <div v-if="!isDay" class="star star1" key="star1"></div>
    <div v-if="!isDay" class="star star2" key="star2"></div>
    <div v-if="!isDay" class="star star3" key="star3"></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  theme: {
    type: String,
    default: 'light',
    validator: (value) => ['light', 'dark'].includes(value),
  },
})

const isDay = computed(() => props.theme === 'light')
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s ease;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.cloud-enter-active,
.cloud-leave-active {
  transition: all 3s ease;
}
.cloud-enter-from,
.cloud-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.SkyTheme {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  z-index: -1;
}

.SkyTheme > .day,
.SkyTheme > .night {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  transition: opacity 1.5s ease-in-out;
}

.day {
  position: relative;
  background: linear-gradient(to bottom, #87ceeb, #e0f7fa);
  width: 100vw;
  height: 100vh;
}

.night {
  position: relative;
  background: linear-gradient(
    to bottom,
    #060010 0%,
    #060010 6%,
    #090016 11%,
    #070016 20%,
    #0a0121 48%,
    #0a0127 55%,
    #0a0129 57%,
    #0c012b 62%,
    #0e0131 68%,
    #0d012f 69%,
    #18023c 78%,
    #19023e 79%,
    #19023e 79%,
    #1c0242 81%,
    #22034b 85%,
    #2e045a 92%,
    #2f045e 96%,
    #340464 98%,
    #370569 100%
  );
  width: 100vw;
  height: 100vh;
}

.cloud1,
.cloud2,
.cloud3,
.cloud4,
.cloud5 {
  position: absolute;
  background-image: url('@/assets/sky/cloud.webp');
  background-size: contain;
  background-repeat: no-repeat;
}

.cloud1 {
  width: 65%;
  height: 40%;

  top: 0%;
  left: 0%;

  animation: moveCloud 30s linear infinite;
}

.cloud2 {
  width: 60%;
  height: 60%;

  top: 25%;
  left: 25%;

  animation: moveCloud 35s linear infinite;
}

.cloud3 {
  width: 80%;
  height: 80%;

  top: 50%;
  left: 50%;

  animation: moveCloud 40s linear infinite;
}

.cloud4 {
  width: 100%;
  height: 100%;

  top: 10%;
  left: 10%;

  animation: moveCloud 80s linear infinite;
}

@keyframes moveCloud {
  0% {
    left: -40%;
  }
  100% {
    left: 100%;
  }
}

.star {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  animation:
    animate 14s ease-in-out infinite,
    backgroudmove 16s linear infinite;
}

.star1 {
  background: url('../assets/sky/star1.webp');
  animation-delay: 0s;
}

.star2 {
  background: url('../assets/sky/star2.webp');
  animation-delay: -1s;
}

.star3 {
  background: url('../assets/sky/star3.webp');
  animation-delay: 1s;
}

@keyframes animate {
  0%,
  20%,
  40%,
  60%,
  80%,
  100% {
    opacity: 0;
  }
  10%,
  30%,
  50%,
  70%,
  90% {
    opacity: 1;
  }
}

@keyframes backgroudmove {
  0% {
    transform: scale(1);
  }
  100% {
    transform: scale(1.1);
  }
}
</style>
