<template>
  <div class="sort-control" v-click-away="closeDropdown">
    <button
      class="sort-trigger"
      @click="toggleDropdown"
      aria-haspopup="true"
      :aria-expanded="isOpen.toString()"
      :aria-controls="dropdownId"
    >
      <span class="sort-icon">
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path d="M3 7H21" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M6 12H18" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
          <path d="M10 17H14" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
        </svg>
      </span>
      <span class="sort-label">{{ t('SortControl.Sorting') }}</span>
      <span class="dropdown-icon" :class="{ 'rotate-180': isOpen }">
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M6 9L12 15L18 9"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </span>
    </button>

    <transition name="fade">
      <div v-if="isOpen" class="sort-dropdown" role="menu" :id="dropdownId">
        <div
          v-for="option in options"
          :key="option.value"
          class="sort-option"
          role="menuitemradio"
          :aria-selected="selectedOption === option.value"
          @click="selectOption(option.value)"
        >
          <input
            type="radio"
            :id="option.value"
            :value="option.value"
            v-model="selectedOption"
            class="sort-radio"
            tabindex="-1"
          />
          <label :for="option.value">{{ option.label }}</label>
        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useSortStore } from '@stores/sortStore.js'

const { t } = useI18n()
const sortStore = useSortStore()
const { selectedOption } = storeToRefs(sortStore)

const isOpen = ref(false)

const options = computed(() => [
  { value: 'date_desc', label: t('SortControl.NewestFirst') },
  { value: 'date_asc', label: t('SortControl.OldestFirst') },
  { value: 'popular', label: t('SortControl.MostPopular') },
])

const dropdownId = ref('sort-dropdown-' + Math.random().toString(36).substr(2, 9))

const toggleDropdown = () => {
  isOpen.value = !isOpen.value
}

const closeDropdown = () => {
  isOpen.value = false
}

const selectOption = (value) => {
  sortStore.setSortOption(value)
  closeDropdown()
}
</script>

<style scoped>
.sort-control {
  position: relative;
  display: inline-block;
  font-size: 0.75rem;
  padding: 0;
  --transition-duration: 0.2s;
}

.sort-trigger {
  display: flex;
  color: var(--text-color);
  align-items: center;
  border: none;
  gap: 8px;
  font-family: inherit;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-duration) ease;
  padding: 6px 12px;
  border-radius: 4px;
  background-color: var(--sort-trigger-bg, transparent);
}

.sort-trigger:hover {
  background-color: var(--sort-trigger-hover-bg, rgba(0, 0, 0, 0.05));
}

.sort-icon svg,
.dropdown-icon svg {
  vertical-align: middle;
  transition: transform var(--transition-duration) ease;
  color: var(--text-color);
}

.dropdown-icon.rotate-180 svg {
  transform: rotate(180deg);
}

.sort-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: var(--sort-dropdown-background-color);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 100000;
  min-width: 200px;
  overflow: hidden;
  border: 1px solid var(--text-color);
}

.sort-option {
  padding: 10px 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  transition: background-color var(--multiselect-tags-background-color) ease;
}

.sort-option:hover {
  background-color: var(--multiselect-new-selection-color);
}

.sort-option[aria-selected='true'] {
  background-color: var(--multiselect-new-selection-color);
}

.sort-radio {
  accent-color: var(--radio-accent-color, var(--header-title-color));
  margin: 0;
}

.sort-option label {
  cursor: pointer;
  font-size: 0.875rem;
  flex-grow: 1;
  user-select: none;
}

/* Transition effects */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity var(--transition-duration) ease,
    transform var(--transition-duration) ease;
  transform-origin: top center;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
</style>
