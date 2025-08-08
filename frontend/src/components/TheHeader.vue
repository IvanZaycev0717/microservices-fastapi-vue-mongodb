<template>
  <div class="TheHeader">
    <HamburgerMenu />
    <div class="header__container" @click="navigateToHome">
      <h1 class="title">{{ t('author') }}</h1>
      <h3>{{ t('job') }}</h3>
    </div>
    <div class="auth-settings__container">
      <UserAuthDialog />
      <div class="settings__container">
        <LanguageSwitcher />
        <ThemeSwitcher />
      </div>
    </div>
  </div>
</template>

<script setup>
import LanguageSwitcher from '@components/LanguageSwitcher.vue'
import ThemeSwitcher from '@components/ThemeSwitcher.vue'
import HamburgerMenu from '@components/HamburgerMenu.vue'
import UserAuthDialog from '@components/UserAuthDialog.vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'

const router = useRouter()

const { t } = useI18n()

const navigateToHome = () => {
  router.push('/')
}
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>
<style>
.TheHeader {
  width: 95%;
  position: sticky;
  z-index: 100;

  display: flex;
  justify-content: space-between;
  align-items: normal;
}

.header__container {
  display: flex;
  flex-direction: column-reverse;
  justify-content: center;
  align-items: flex-start;
  color: var(--text-color);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.header__container:hover {
  transform: translateY(-2px);
}

.title {
  color: var(--text-color);
  transition: all 0.5s ease;
}

.header__container:hover .title {
  background: linear-gradient(
    90deg,
    var(--text-color),
    var(--header-title-color),
    var(--text-color)
  );
  background-size: 200% auto;
  color: transparent;
  -webkit-background-clip: text;
  background-clip: text;
  animation: shimmer 1.5s infinite linear;
}

@keyframes shimmer {
  0% {
    background-position: 0% center;
  }
  100% {
    background-position: -200% center;
  }
}

.auth-settings__container {
  display: flex;
  flex-direction: column;
  width: 200px;
}

.settings__container {
  display: flex;
  flex-direction: row;
  margin-top: 0.5vh;
  gap: 5px;
}

/* Переопределение vue-multiselect */
.multiselect__tags {
  background: var(--multiselect-tags-background-color);
}

.multiselect__content-wrapper {
  background-color: var(--multiselect-conten-wrapper-background-color);
}

.multiselect__option--selected {
  background-color: var(--multiselect-conten-wrapper-background-color);
}

.multiselect__single {
  background-color: var(--multiselect-single-background-color);
}

.multiselect__option--highlight {
  background: var(--multiselect-new-selection-color);
  outline: none;
}

.multiselect__option--selected.multiselect__option--highlight {
  background: var(--multiselect-new-selection-color);
  color: var(--multiselect-tags-background-color);
}

@media (max-width: 768px) {
  .TheHeader {
    width: 92%;
    align-items: center;
    justify-content: center;
  }
  .header__container {
    width: 100%;
    margin-left: 20px;
  }

  .auth-settings__container {
    display: none;
  }
}
</style>
