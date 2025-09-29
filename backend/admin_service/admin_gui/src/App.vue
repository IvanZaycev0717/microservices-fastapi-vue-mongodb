<template>
  <router-view />
</template>

<script setup>
// import { onMounted } from 'vue'
// import { useAuthStore } from 'stores/auth'
// import { useRouter, useRoute } from 'vue-router'
// import { api } from 'boot/axios'
// import { useQuasar } from 'quasar'

// const authStore = useAuthStore()
// const router = useRouter()
// const route = useRoute()
// const $q = useQuasar()

// onMounted(async () => {
//   if (!authStore.accessToken && route.path !== '/login') {
//     try {
//       const response = await api.post('/auth/refresh', {}, { 
//         withCredentials: true 
//       })
//       authStore.setToken(response.data.access_token)
//       $q.notify({
//         type: 'positive',
//         message: 'Session restored automatically',
//         position: 'top',
//         timeout: 1000
//       })
//       if (route.path === '/') {
//         router.push('/')
//       }
//     } catch (error) {
//       $q.notify({
//         type: 'negative',
//         message: error,
//         position: 'top',
//         timeout: 1000
//       })
//     }
//   }
// })
</script>