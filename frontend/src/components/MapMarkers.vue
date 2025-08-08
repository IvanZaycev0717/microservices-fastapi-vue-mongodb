<template>
  <div class="map-markers-container">
    <svg
      class="map-markers"
      xmlns="http://www.w3.org/2000/svg"
      :viewBox="viewBox"
      preserveAspectRatio="xMidYMid meet"
    >
      <path
        id="backend_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'backend_kingdom',
          highlight: highlightedMarker === 'backend_kingdom',
        }"
        d="M165.63,256.1c22.93-31.69,46.51-64.01,78.7-86.23,48.22-33.28,109.64-39.86,168.2-41.57,75.06-2.18,154.43,3.25,217.15,44.55,32.29,21.26,58.12,50.78,83.53,79.92,43.74,50.16,89.27,104.02,99.79,169.73,6.22,38.83-.48,78.72,4.24,117.76,8.12,67.11,49.11,126.33,60.76,192.91,10.44,59.68-4.4,123.37-40.13,172.3-41.88,57.34-109.05,92.07-178.13,108.49s-140.86,16.35-211.86,16.19c-66.72-.15-133.44-.3-200.16-.44-46.77-.1-95.79-.76-136.8-23.24-42.14-23.09-69.94-66.73-84.14-112.64-14.21-45.9-16.41-94.53-18.51-142.53-2.49-56.96-4.98-113.92-7.47-170.88-1.26-28.88-2.39-58.7,7.86-85.74,17.12-45.18,60.49-70.61,86.45-109.56,13.09-19.63,10.51-35.78,17.88-55.52,9.51-25.46,36.71-51.49,52.65-73.5Z"
        @mouseenter="(e) => handleMouseEnter('backend_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('backend_kingdom')"
      />

      <path
        id="frontend_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'frontend_kingdom',
          highlight: highlightedMarker === 'frontend_kingdom',
        }"
        d="M1086.35,476.43c19.44-54.41,37.57-116.37,88.01-144.53,31.2-17.41,68.7-17.89,104.42-17.93,97.97-.11,195.94-.22,293.91-.32,58.77-.07,118.48,0,174.88,16.51,47.39,13.87,94.43,42.88,111.34,89.27,7.41,20.31,8.46,42.38,7.78,63.98-5.5,174.62-115.65,326.19-221.21,465.39-18.85,24.87-37.98,50.01-62.38,69.46-38.95,31.05-88.35,45.31-136.61,57.64-68.3,17.46-138.41,32.58-208.73,27.62s-141.79-32.46-186.14-87.26c-58.75-72.61-58.93-174.72-87.75-263.57-4.22-13.01-9.16-26.33-7.88-39.95,2.65-28.23,52.94-74.71,67.96-100.94,24.73-43.18,45.65-88.53,62.39-135.38Z"
        @mouseenter="(e) => handleMouseEnter('frontend_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('frontend_kingdom')"
      />
      <path
        id="database_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'database_kingdom',
          highlight: highlightedMarker === 'database_kingdom',
        }"
        d="M1921.27,687.81c16.27-22.4,28.21-48.89,50.38-65.47,12.95-9.68,28.5-15.23,44.11-19.42,72.26-19.39,151.49-11.52,218.53,21.71,67.04,33.22,121.29,91.5,149.63,160.74,10.89,26.61,18.03,54.57,25.14,82.43,22.08,86.57,44.16,173.14,66.24,259.71,11.34,44.44,20.85,97.22-9.62,131.51-20.36,22.91-52.55,29.95-81.23,40.77-56.8,21.44-104.6,61.04-157.41,91-100.8,57.2-217.63,78.17-332.25,95.32-77.75,11.64-159.72,21.51-232.9-7.21-110.67-43.43-173.04-168.53-173.73-287.42-.11-18.6,1.3-38.11,11.11-53.92,7.08-11.41,18.02-19.94,29.59-26.78,44.41-26.24,101.27-31.41,138.22-67.41,21.42-20.87,33.15-49.43,45.22-76.78,27.04-61.27,58.23-121.25,94.35-177.68,29.1-45.46,82.1-56.35,114.62-101.11Z"
        @mouseenter="(e) => handleMouseEnter('database_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('database_kingdom')"
      />
      <path
        id="desktop_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'desktop_kingdom',
          highlight: highlightedMarker === 'desktop_kingdom',
        }"
        d="M2475.07,657.81c31.87,8.27,63.73,16.54,95.6,24.81,79.73,20.69,162.81,41.51,243.58,25.31,31.11-6.24,60.87-17.84,90.19-30,49.12-20.38,98.43-43.09,137.54-79.12,39.11-36.03,67.03-87.8,62.47-140.78-1.26-14.65-5.12-29.42-13.66-41.39-24.2-33.88-73.5-33.36-112.65-47.51-63.27-22.86-101.71-86.85-125.86-149.65-24.15-62.79-40.08-130.49-80.9-183.96-9.13-11.96-19.82-23.35-33.59-29.42-12.27-5.41-26.04-6.2-39.45-6.1-73.73.55-145.04,25.26-213.32,53.1-31.08,12.67-62.05,26.16-90.09,44.59-84.25,55.38-133.85,149.03-179.95,238.69-6,11.67-12.09,23.63-13.78,36.64-8.4,64.75,75.82,98.78,86.54,158.84,3.9,21.87-3.88,23.25,11.3,43.15,12.24,16.05,33.67,28.18,50.96,37.81,38.77,21.59,82.38,33.89,125.08,44.97Z"
        @mouseenter="(e) => handleMouseEnter('desktop_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('desktop_kingdom')"
      />
      <path
        id="devops_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'devops_kingdom',
          highlight: highlightedMarker === 'devops_kingdom',
        }"
        d="M2594.27,1208.76c-15.52-22.59-27.46-48.67-27.92-76.08-.94-56.52,46.19-102.56,95.93-129.41s106-42.62,150.11-77.97c15.72-12.6,29.5-27.4,43.23-42.14,23.7-25.46,47.4-50.92,71.1-76.38,45.47-48.84,90.93-97.68,136.38-146.54,15.02-16.15,30.3-32.51,49.17-43.93,22.97-13.9,49.82-19.63,76.1-25.14,11.63-2.44,23.5-4.89,35.3-3.51,32.24,3.75,54,33.7,71.63,60.95,14.51,22.43,29.35,45.68,33.77,72.03,4.37,26.09-1.89,53.13,2.87,79.15,9.46,51.78,59.31,86.11,108.44,104.99,49.13,18.88,102.87,28.96,145.36,60.03,78.72,57.54,95.13,170.65,75.52,266.17-4.73,23.05-11.23,45.98-22.42,66.68-33.48,61.95-103.91,95.1-172.91,109.12-179.62,36.5-365.02-29.3-547.79-15.48-32.11,2.43-68.14,7.7-99.17-3.7s-42.5-37.31-64.77-59.48c-48.97-48.75-117.41-57.44-159.94-119.35Z"
        @mouseenter="(e) => handleMouseEnter('devops_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('devops_kingdom')"
      />
      <path
        id="telegram_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'telegram_kingdom',
          highlight: highlightedMarker === 'telegram_kingdom',
        }"
        d="M3409.58,722.5c47.68,39.5,100.65,73.92,159.7,92.55,59.05,18.63,124.81,20.46,181.89-3.53,45.62-19.17,83.06-53.25,119.53-86.7,49.53-45.43,102.44-97.47,107.79-164.47,1.88-23.48-2.55-47.44-12.69-68.69-19.25-40.35-57.48-68.7-97.99-87.61-40.51-18.9-84.2-29.89-126.01-45.72-74.06-28.04-143.16-71.55-221.2-84.95-27.41-4.7-55.33-5.56-83.15-5.63-57.15-.15-118.51,4.45-163.23,40.03-45.03,35.83-63.65,101.43-44.15,155.57,17.63,48.95,59.91,83.37,81.58,130.12,24.52,52.89,51.97,90.95,97.94,129.03Z"
        @mouseenter="(e) => handleMouseEnter('telegram_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('telegram_kingdom')"
      />
      <path
        id="parsing_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'parsing_kingdom',
          highlight: highlightedMarker === 'parsing_kingdom',
        }"
        d="M768.4,1695.61c-24.56,72.97-93.41,124.05-166.82,147.26-73.41,23.21-151.9,22.89-228.89,22.35-90.2-.63-180.4-1.27-270.59-1.9-6.66-.05-13.81-.24-19.22-4.13-5.97-4.29-8.29-11.95-10.23-19.05-11.8-43.16-23.61-86.32-35.41-129.49-13.49-49.32-27.08-99.47-26.08-150.58,1.29-66.1,26.82-129.05,52.71-189.88,19.74-46.4,41.03-94.17,78.77-127.62,61.23-54.26,150.54-58.77,232.34-60.48,59.77-1.25,120.61-2.37,178.07,14.13,82.21,23.61,151.92,83,195.63,156.52s62.55,160.23,61.91,245.76c-.4,54.14-14.98,117.49-64.75,138.82"
        @mouseenter="(e) => handleMouseEnter('parsing_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('parsing_kingdom')"
      />
      <path
        id="computerscience_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'computerscience_kingdom',
          highlight: highlightedMarker === 'computerscience_kingdom',
        }"
        d="M2110.03,1983.81c-62.05-41.54-83.75-125.83-71.39-199.48,12.35-73.65,52.4-139.31,92.47-202.33,13.19-20.74,26.58-41.57,43.58-59.32,33.1-34.57,77.62-55.34,119.92-77.74,49.55-26.24,97.56-55.84,140.61-91.75,30.62-25.54,60.45-55.2,99.12-64.94,39.27-9.89,80.32,2.68,118.83,15.22,12.38,4.03,25.01,8.2,35.45,15.99,26.94,20.08,32.21,57.61,48.38,87.07,34.12,62.18,112.05,82.54,169.36,124.31,55.78,40.65,92.68,103.48,111.85,169.78,19.17,66.31,21.85,136.29,19.32,205.27-.84,22.99-2.43,46.66-12.55,67.31-19.08,38.9-63.21,57.86-104.53,70.89-205.71,64.89-425.91,60.98-641.56,56.45-14.32-.3-29.58-.89-41.32-9.08-25.13-17.52-27.39-55.21-50.19-74.27-21.19-17.71-53.72-17.63-77.33-33.37Z"
        @mouseenter="(e) => handleMouseEnter('computerscience_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('computerscience_kingdom')"
      />
      <path
        id="gamedev_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'gamedev_kingdom',
          highlight: highlightedMarker === 'gamedev_kingdom',
        }"
        d="M1511.64,2113.79c-85.59-3.22-169.72-24.28-255.29-28.22-40.12-1.84-80.35.09-120.45-2.08-107.53-5.82-213.27-41.85-301.99-102.9-13.41-9.23-26.85-19.48-34.52-33.84-6.01-11.24-8.01-24.19-8.69-36.92-6.35-118.61,90.58-217.38,115.87-333.43,8.25-37.84,8.7-76.99,15.89-115.05,7.54-39.85,22.52-78.29,43.95-112.72,9.89-15.89,21.24-31.05,35.4-43.29,31.47-27.21,73.72-37.65,114.43-46.21,94.36-19.83,191.55-34.15,287.02-20.67,32.79,4.63,69.12,15.5,84.14,45.01,7.94,15.61,8.38,33.78,10.05,51.22,9.64,100.42,68.55,194.94,154.47,247.82,29.35,18.06,61.88,31.74,87.17,55.16,36.48,33.78,53.22,83.25,68.32,130.63,15.4,48.34,30.68,98.42,25.48,148.89-7.04,68.3-59.37,105.95-110,143.82-59.2,44.28-139.28,55.49-211.26,52.78Z"
        @mouseenter="(e) => handleMouseEnter('gamedev_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('gamedev_kingdom')"
      />
      <path
        id="ai_kingdom"
        class="map-marker"
        :class="{
          active: activeMarker === 'ai_kingdom',
          highlight: highlightedMarker === 'ai_kingdom',
        }"
        d="M3360.8,1465.8c12.97-8.28,26.31-16.49,41.18-20.45,12.97-3.46,26.57-3.55,39.99-3.61,32.43-.15,64.86-.31,97.29-.46,41.1-.19,82.61-.34,122.7,8.72,75,16.96,139.55,65.08,192.78,120.58,40.1,41.8,75.79,89.62,93.01,144.93,17.22,55.31,13.8,119.16-19.27,166.72-32.31,46.47-87.1,71.27-140.21,90.83-57.3,21.1-115.9,38.65-175.36,52.53-50.45,11.78-102.95,20.92-153.84,11.21-85.26-16.27-152.23-82.21-233.47-112.79-32.13-12.09-69.89-21.29-86.44-51.36-9.77-17.76-9.67-39.09-9.31-59.35.69-39.07,1.38-78.14,2.06-117.21,1.12-63.62,24.74-79.4,70.52-115.3,51.49-40.39,103.14-79.72,158.37-114.97Z"
        @mouseenter="(e) => handleMouseEnter('ai_kingdom', e)"
        @mouseleave="handleMouseLeave"
        @click="handleClick('ai_kingdom')"
      />
    </svg>

    <Teleport to="body">
      <div
        v-if="activeTooltip"
        class="custom-tooltip"
        :class="{ show: activeTooltip }"
        :style="{
          left: tooltipPosition.x + 'px',
          top: tooltipPosition.y + 'px',
        }"
      >
        {{ tooltipContent }}
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const activeTooltip = ref(null)
const tooltipContent = ref('')
const tooltipPosition = ref({ x: 0, y: 0 })

defineProps({
  viewBox: {
    type: String,
    default: '0 0 4096 2339',
  },
})

const emit = defineEmits(['marker-click'])

const activeMarker = ref(null)
const highlightedMarker = ref(null)

const handleHover = (markerId, event) => {
  const TOOLTIP_WIDTH = 200
  const TOOLTIP_HEIGHT = 60

  const tooltips = {
    backend_kingdom: t('MapMarkers.Backend'),
    frontend_kingdom: t('MapMarkers.Frontend'),
    database_kingdom: t('MapMarkers.Databases'),
    desktop_kingdom: t('MapMarkers.Desktop'),
    devops_kingdom: t('MapMarkers.DevOps'),
    telegram_kingdom: t('MapMarkers.Telegram'),
    parsing_kingdom: t('MapMarkers.Parsing'),
    computerscience_kingdom: t('MapMarkers.ComputerScience'),
    gamedev_kingdom: t('MapMarkers.GameDev'),
    ai_kingdom: t('MapMarkers.AI'),
  }

  tooltipContent.value = tooltips[markerId] || markerId

  tooltipContent.value = tooltips[markerId] || markerId

  let x = event.clientX - TOOLTIP_WIDTH / 2
  let y = event.clientY - TOOLTIP_HEIGHT / 2

  x = Math.max(0, Math.min(x, window.innerWidth - TOOLTIP_WIDTH))
  y = Math.max(0, Math.min(y, window.innerHeight - TOOLTIP_HEIGHT))

  tooltipPosition.value = { x, y }
}

const handleMouseEnter = (markerId, event) => {
  highlightedMarker.value = markerId
  activeTooltip.value = markerId
  handleHover(markerId, event)
}

const handleMouseLeave = () => {
  activeTooltip.value = null
  highlightedMarker.value = null
}

const handleClick = (markerId) => {
  activeMarker.value = markerId
  emit('marker-click', markerId)
  setTimeout(() => {
    activeMarker.value = null
  }, 700)
}

const setActiveMarker = (markerId) => {
  activeMarker.value = markerId
}

defineExpose({
  setActiveMarker,
})
</script>

<style scoped>
.map-markers-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.map-markers {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: all;
}

.map-marker {
  stroke: none;
  fill: transparent;
  cursor: pointer;
  transition: all 0.2s ease;

  &:active {
    transform: scale(0.996);
    transition-duration: 0.05s;
  }
}

.custom-tooltip {
  position: fixed;
  z-index: 10000;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  font-size: 14px;
  pointer-events: none;
  transform: translate(10px, -100%);
  max-width: 200px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
}
</style>
