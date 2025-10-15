<template>
  <div
    class="map-container"
    ref="mapContainer"
    @wheel.prevent="handleWheel"
    @mousedown="startDrag"
    @mousemove="handleDrag"
    @mouseup="endDrag"
    @mouseleave="endDrag"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd"
  >
    <Teleport to="body">
      <Transition name="fade">
        <SkillsModal v-if="showModal" @close="showModal = false" :show="showModal">
          <template #title>
            <h2>{{ chosenSkill.kingdom }}</h2>
          </template>

          <template #skills_list>
            <div class="skills-container">
              <div class="skill-category">
                <ul>
                  <li v-for="(item, index) in chosenSkill.items" :key="index">
                    {{ item }}
                  </li>
                </ul>
              </div>
            </div>
          </template>
        </SkillsModal>
      </Transition>
    </Teleport>
    <div
      class="map-content"
      :style="{
        transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
        'transform-origin': '0 0',
      }"
    >
      <img
        :src="mapImage"
        alt="Map Background"
        class="map-background"
        draggable="false"
        ref="mapImageRef"
      />
      <MapMarkers class="map-markers" @marker-click="handleClick" />
    </div>

    <div class="map-controls">
      <button @click="zoomIn">+</button>
      <button @click="zoomOut">-</button>
      <button @click="resetZoom">Reset</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import mapImageUrl from '@assets/TechMap/map.webp'
import MapMarkers from '@components/MapMarkers.vue'
import SkillsModal from '@components/SkillsModal.vue'

import { useSkills } from '@composables/useSkills.js'

const [skillsData, fetchTechData, loading, error] = useSkills()

const mapImage = mapImageUrl
const scale = ref(1)
const position = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const mapContainer = ref(null)
const mapImageRef = ref(null)

const chosenSkill = ref(null)
const showModal = ref(false)

onMounted(() => {
  fetchTechData()

  if (mapImageRef.value) {
    mapImageRef.value.onload = () => {}
  }
})

const handleClick = (markerId) => {
  chosenSkill.value = skillsData.value[markerId]
  showModal.value = true
}

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.2, 3)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.2, 0.5)
}

const resetZoom = () => {
  scale.value = 1
  position.value = { x: 0, y: 0 }
}

const handleWheel = (e) => {
  e.preventDefault()
  const delta = -Math.sign(e.deltaY)
  const newScale = Math.min(Math.max(scale.value + delta * 0.1, 0.5), 3)

  const rect = mapContainer.value.getBoundingClientRect()
  const mouseX = e.clientX - rect.left
  const mouseY = e.clientY - rect.top

  position.value.x = mouseX - (mouseX - position.value.x) * (newScale / scale.value)
  position.value.y = mouseY - (mouseY - position.value.y) * (newScale / scale.value)

  scale.value = newScale
}

const startDrag = (e) => {
  if (e.button !== 0) return
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - position.value.x,
    y: e.clientY - position.value.y,
  }
}

const handleDrag = (e) => {
  if (!isDragging.value) return
  position.value = {
    x: e.clientX - dragStart.value.x,
    y: e.clientY - dragStart.value.y,
  }
}

const endDrag = () => {
  isDragging.value = false
}

const handleTouchStart = (e) => {
  if (e.touches.length === 1) {
    isDragging.value = true
    dragStart.value = {
      x: e.touches[0].clientX - position.value.x,
      y: e.touches[0].clientY - position.value.y,
    }
  }
}

const handleTouchMove = (e) => {
  if (!isDragging.value || e.touches.length !== 1) return
  e.preventDefault()
  position.value = {
    x: e.touches[0].clientX - dragStart.value.x,
    y: e.touches[0].clientY - dragStart.value.y,
  }
}

const handleTouchEnd = () => {
  isDragging.value = false
}
</script>

<style scoped>
.map-container {
  position: relative;
  width: 100%;
  height: 55vh;
  min-height: 300px;
  overflow: hidden;
  cursor: grab;
  user-select: none;
  touch-action: none;
  border: 1px solid black;
  border-radius: 5px;
  background-color: var(--selection-color);
}

.map-content {
  position: absolute;
  width: 100%;
  height: 100%;
  transition: transform 0.1s ease-out;
}

.map-background {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: contain;
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

.map-container:active {
  cursor: grabbing;
}

.map-controls {
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 10;
}

.map-controls button {
  padding: 8px 16px;
  background: var(--button-background-color);
  border: 1px solid black;
  border-radius: 4px;
  cursor: pointer;
  font-family: 'MyFont', sans-serif;
  font-size: 1.1rem;
  color: var(--text-color);
}

.map-controls button:hover {
  background: var(--hover-button-background-color);
}

:deep(.map-marker) {
  transition: all 0.2s ease;
  cursor: pointer;
}

:deep(.map-marker:hover),
:deep(.map-marker.active) {
  fill: var(--map-hover-color);
  stroke: none;
  stroke-width: 2;
}

@media (hover: none) {
  :deep(.map-marker) {
    fill: var(--map-hover-color);
  }
}

.skill-category ul {
  list-style-type: none;
  padding-left: 0;
}

.skill-category li {
  position: relative;
  padding-left: 1.5em;
  margin-bottom: 0.5em;
  font-weight: bold;
}

.skill-category li::before {
  content: '✔️';
  position: absolute;
  left: 0;
}
</style>
<style>
.fade-enter-active {
  transition: opacity 0.4s ease;
}

.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
