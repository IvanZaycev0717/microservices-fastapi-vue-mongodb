const routes = [
  {
    path: '/login',
    component: () => import('pages/LoginPage.vue'),
  },
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      {
        path: '',
        component: () => import('pages/IndexPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: '/about',
        component: () => import('pages/AboutPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: '/tech',
        component: () => import('pages/TechPage.vue'),
        meta: { requiresAuth: true },
      },
      {
        path: '/projects',
        component: () => import('pages/ProjectsPage.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },

  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
]

export default routes
