<template>
  <q-layout>
    <q-header elevated>
      <q-toolbar>
        <q-btn
          flat
          dense
          round
          icon="menu"
          aria-label="Menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />
        <q-toolbar-title>IvanZaycev0717 | Personal Site Microservices | Admin GUI</q-toolbar-title>

        <q-btn href="https://github.com/IvanZaycev0717/" target="_blank" flat>
          <GitHubIcon />
        </q-btn>
        <q-btn href="https://t.me/ivanzaycev0717" target="_blank" flat>
          <TelegramIcon />
        </q-btn>

        <q-btn
          :icon="$q.dark.isActive ? 'light_mode' : 'dark_mode'"
          @click="$q.dark.toggle()"
          flat
        />
        <q-btn icon="logout" @click="handleLogout" flat label="Logout" />
      </q-toolbar>
    </q-header>

    <SideBarPanel v-model="leftDrawerOpen" />

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup>
import { ref } from 'vue'
import GitHubIcon from 'components/icons/GitHubIcon.vue'
import TelegramIcon from 'components/icons/TelegramIcon.vue'
import SideBarPanel from 'components/SideBarPanel.vue'
import { useQuasar } from 'quasar'
import { watchEffect } from 'vue'
import { useAuthStore } from 'stores/auth'
import { logoutUser } from 'boot/axios'

const $q = useQuasar()
const leftDrawerOpen = ref(false)
const darkMode = JSON.parse(localStorage.getItem('darkMode') || 'false')
const authStore = useAuthStore()

$q.dark.set(darkMode)

watchEffect(() => {
  localStorage.setItem('darkMode', JSON.stringify($q.dark.isActive))
})

const handleLogout = async () => {
  try {
    await logoutUser()
  } catch (error) {
     $q.notify({
      type: 'negative',
      message: `Logout warning: ${error.response?.data?.detail || 'Proceeding with local logout'}`,
    })
  }
  
  authStore.clearToken()
  window.location.href = '/login'
}
</script>