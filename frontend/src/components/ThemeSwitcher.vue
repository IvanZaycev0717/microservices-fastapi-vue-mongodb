<template>
  <div class="theme-selector">
    <label for="theme-select" class="visually-hidden">
      {{ t('ThemeSelector.Label') }}
    </label>

    <multiselect
      id="theme-select"
      class="theme__container"
      :placeholder="''"
      :show-labels="false"
      :searchable="false"
      :allow-empty="false"
      :custom-label="customLabel"
      v-model="selectedTheme"
      :options="themeOptions"
      label="name"
      track-by="code"
      :aria-label="t('ThemeSelector.Label')"
      :aria-describedby="themeDescriptionId"
      @update:modelValue="handleThemeChange"
    >
      <template #option="{ option }">
        <div class="theme-option__container" role="option">
          <div class="theme-icon__container">
            <component :is="option.img" class="theme-svg" aria-hidden="true" />
          </div>
          <span class="visually-hidden">
            {{ t(`ThemeSelector.Options.${option.code}`) }}
          </span>
        </div>
      </template>

      <template #singleLabel="{ option }">
        <div class="selected-option">
          <div class="theme-icon__container">
            <component :is="option.img" class="theme-svg" aria-hidden="true" />
          </div>
          <span class="visually-hidden">
            {{ t(`ThemeSelector.Options.${option.code}`) }}
          </span>
        </div>
      </template>
    </multiselect>

    <span :id="themeDescriptionId" class="visually-hidden">
      {{ t('ThemeSelector.Description') }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed, inject } from 'vue'
import { useI18n } from 'vue-i18n'
import Multiselect from 'vue-multiselect'
import DarkThemeIcon from '@icons/DarkThemeIcon.vue'
import LightThemeIcon from '@icons/LightThemeIcon.vue'

const { t } = useI18n()
const { currentTheme, toggleTheme } = inject('theme')

const themeDescriptionId = ref('theme-desc-' + Math.random().toString(36).substr(2, 9))

const themeOptions = ref([
  {
    code: 'light',
    name: 'Light',
    img: LightThemeIcon,
  },
  {
    code: 'dark',
    name: 'Dark',
    img: DarkThemeIcon,
  },
])

const selectedTheme = computed({
  get: () => themeOptions.value.find((opt) => opt.code === currentTheme.value),
  set: (newTheme) => {
    if (newTheme.code !== currentTheme.value) {
      toggleTheme()
    }
  },
})

const customLabel = ({ name, code }) => {
  return `${name} (${code})`
}

const handleThemeChange = (selected) => {
  if (selected.code !== currentTheme.value) {
    toggleTheme()
  }
}
</script>

<style>
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.theme-selector {
  position: relative;
  width: 100%;
}

.theme-option__container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  cursor: pointer;
}

.theme-icon__container {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.theme-svg {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.1);
}

.selected-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.multiselect__option--highlight {
  background: var(--theme-select-highlight);
}

.multiselect__option--selected {
  background: var(--theme-select-selected);
}
</style>
