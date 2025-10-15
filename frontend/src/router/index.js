import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@stores/authStore.js'
import { getConfig } from '@utils/config'

const router = createRouter({
  history: createWebHistory(getConfig('BASE_URL')),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@views/HomeView.vue'),
      alias: '/home',
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@views/AboutMeView.vue'),
    },
    {
      path: '/technologies',
      name: 'technologies',
      component: () => import('@views/TechnologiesView.vue'),
    },
    {
      path: '/projects',
      name: 'projects',
      component: () => import('@views/ProjectsView.vue'),
    },
    {
      path: '/certificates',
      name: 'certificates',
      component: () => import('@views/CertificatesView.vue'),
    },
    {
      path: '/publications',
      name: 'publications',
      component: () => import('@views/PublicationsView.vue'),
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: () => import('@views/ContactsView.vue'),
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('@views/AccountView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/reset_password',
      name: 'reset_password',
      component: () => import('@views/ResetPasswordView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('@views/NotFound.vue'),
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth',
      }
    } else {
      return { top: 0 }
    }
  },
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/')
  } else {
    next()
  }
})

export default router
