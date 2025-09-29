import { defineRouter } from '#q-app/wrappers'
import { useAuthStore } from 'stores/auth'
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from 'vue-router'
import routes from './routes'

export default defineRouter(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === 'history'
      ? createWebHistory
      : createWebHashHistory

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes,
    history: createHistory(process.env.VUE_ROUTER_BASE),
  })

  Router.beforeEach(async (to) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth && !authStore.accessToken) {
      const success = await authStore.tryRefresh()
      if (!success) return '/login'
    }

    if (to.path === '/login' && authStore.accessToken) {
      return '/'
    }
  })

  return Router
})
