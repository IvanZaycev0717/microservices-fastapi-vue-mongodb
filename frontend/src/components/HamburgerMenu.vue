<template>
  <button
    class="HamburgerMenu"
    :class="{ 'HamburgerMenu--active': isMenuOpen }"
    @click="toggleMenu"
    aria-label="Меню"
    aria-expanded="isMenuOpen"
  >
    <span class="HamburgerMenu__line" :class="{ 'HamburgerMenu__line--active': isOpen }"></span>
    <span class="HamburgerMenu__line" :class="{ 'HamburgerMenu__line--active': isOpen }"></span>
    <span class="HamburgerMenu__line" :class="{ 'HamburgerMenu__line--active': isOpen }"></span>
  </button>

  <div v-if="isMenuOpen" class="menu-overlay" @click="closeMenu"></div>

  <aside class="menu-drawer" :class="{ 'menu-drawer--open': isMenuOpen }">
    <nav class="menu-nav">
      <ul>
        <li
          v-for="button in translatedButtons"
          :key="button.translationKey"
          @click="navigateTo(button.routerName)"
        >
          <SidebarButton>
            <component :is="button.icon" />
            {{ button.text }}
          </SidebarButton>
        </li>
      </ul>
      <hr />
      <ul>
        <li><ThemeSwitcher /></li>
        <li><LanguageSwitcher /></li>
      </ul>
      <hr />
      <ul>
        <li><UserAuthDialog /></li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useNavigation } from '@composables/useNavigation'

import SidebarButton from '@components/SidebarButton.vue'
import ThemeSwitcher from '@components/ThemeSwitcher.vue'
import LanguageSwitcher from '@components/LanguageSwitcher.vue'
import UserAuthDialog from '@components/UserAuthDialog.vue'

const router = useRouter()
const { translatedButtons } = useNavigation()

const isMenuOpen = ref(false)

const navigateTo = (routerName) => {
  router.push({ name: routerName })
  closeMenu()
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
}
</script>

<style scoped>
.HamburgerMenu {
  display: none;
  position: relative;
  z-index: 800;
  width: 60px;
  height: 55px;

  background: var(--button-background-color);
  border: 2px solid black;
  border-radius: 4px;
  cursor: pointer;
}

.HamburgerMenu:hover {
  background: var(--hover-button-background-color);
}

@media (max-width: 768px) {
  .HamburgerMenu {
    display: flex;
    flex-direction: column;
    justify-content: space-around;
  }
}

.HamburgerMenu__line {
  width: 100%;
  height: 4px;
  background: var(--hamburger-line-color);
  transition: transform 0.3s opacity ease;
}

.HamburgerMenu__line--active:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.HamburgerMenu__line--active:nth-child(2) {
  opacity: 0;
}

.HamburgerMenu__line--active:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}

.menu-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  z-index: 900;
}

.menu-drawer {
  position: fixed;
  top: 0;
  left: -100%;
  width: 250px;
  height: 100%;
  background: var(--hover-button-background-color);
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  z-index: 950;
  transition: left 0.3s ease;
  overflow-y: auto;
}

.menu-drawer--open {
  left: 0;
}

.menu-nav hr {
  width: 90%;
  border: none;
  height: 2px;
  background: var(--button-background-color);
  box-shadow:
    0 1px 1px rgba(255, 255, 255, 0.3) inset,
    0 -1px 1px rgba(0, 0, 0, 0.1) inset;
}

.menu-nav ul {
  padding: 20px 20px 5px 20px;
  list-style: none;
}

.menu-nav li {
  margin-bottom: 12px;
}

.menu-nav a {
  text-decoration: none;
  color: #333;
  font-size: 18px;
  font-weight: bold;
}
</style>
