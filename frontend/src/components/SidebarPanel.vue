<template>
  <div class="SidebarPanel">
    <SidebarButton
      v-for="button in translatedButtons"
      :key="button.translationKey"
      @click="navigateTo(button.routerName)"
      :disabled="isActive(button.routerName)"
    >
      <component :is="button.icon" />
      {{ button.text }}
    </SidebarButton>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import SidebarButton from '@components/SidebarButton.vue'
import { useNavigation } from '@composables/useNavigation'

const router = useRouter()
const route = useRoute()
const { translatedButtons } = useNavigation()

const navigateTo = (routerName) => {
  if (!isActive(routerName)) {
    router.push({ name: routerName })
  }
}

const isActive = (routerName) => {
  return route.name === routerName
}
</script>

<style scoped>
.SidebarPanel {
  width: 25vw;
  height: 65vh;
  padding: 20px;
  box-sizing: border-box;

  position: sticky;
  overflow-y: auto;

  display: flex;
  flex-direction: column;
  justify-content: space-around;
  align-items: center;
  align-content: stretch;

  background-image: var(--sidebar-background-image);
  background-repeat: no-repeat;
  background-size: contain;
  background-position: center;
  background-blend-mode: lighten;
  background-color: var(--sidebar-background-color);

  border: var(--sidebar-border);
  border-radius: 10px;
}

.SidebarPanel::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
}

@media (max-width: 768px) {
  .SidebarPanel {
    display: none;
  }
}
</style>
