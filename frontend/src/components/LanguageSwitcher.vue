<template>
  <div class="language-selector">
    <!-- Добавляем визуально скрытый, но доступный label -->
    <label for="language-select" class="visually-hidden">
      {{ t('LanguageSelector.Label') }}
    </label>

    <multiselect
      id="language-select"
      class="language__container"
      :placeholder="''"
      :show-labels="false"
      :searchable="false"
      :allow-empty="false"
      :custom-label="customLabel"
      v-model="language"
      :options="languageOptions"
      label="name"
      track-by="code"
      :aria-label="t('LanguageSelector.Label')"
      :aria-describedby="languageDescriptionId"
    >
      <template #option="{ option }">
        <div class="option__container">
          <component :is="option.img" class="flag-svg" aria-hidden="true" />
          <span class="visually-hidden">{{ option.name }}</span>
        </div>
      </template>

      <template #singleLabel="{ option }">
        <div class="selected-option">
          <component :is="option.img" class="flag-svg" aria-hidden="true" />
          <span class="visually-hidden">{{ option.name }}</span>
        </div>
      </template>
    </multiselect>

    <!-- Скрытое описание для скринридеров -->
    <span :id="languageDescriptionId" class="visually-hidden">
      {{ t('LanguageSelector.Description') }}
    </span>
  </div>
</template>

<script setup>
import { ref, computed, markRaw } from 'vue'
import Multiselect from 'vue-multiselect'
import { useLanguageStore } from '@stores/languageStore.js'
import { useI18n } from 'vue-i18n'
import UKFlagIcon from '@icons/UKFlagIcon.vue'
import RussianFlagIcon from '@icons/RussianFlagIcon.vue'

const { t } = useI18n()
const languageStore = useLanguageStore()

// Генерируем уникальный ID для описания
const languageDescriptionId = ref('language-desc-' + Math.random().toString(36).substr(2, 9))

const languageOptions = ref([
  {
    code: 'en',
    name: 'English',
    img: markRaw(UKFlagIcon),
  },
  {
    code: 'ru',
    name: 'Русский',
    img: markRaw(RussianFlagIcon),
  },
])

const language = computed({
  get: () => languageOptions.value.find((opt) => opt.code === languageStore.language),
  set: (val) => languageStore.setLanguage(val.code),
})

const customLabel = ({ name, code }) => {
  return `${name} (${code})`
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

.language-selector {
  position: relative;
  width: 100%;
}

.option__container {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
}

.selected-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.flag-svg {
  width: 24px;
  height: 24px;
}
</style>
