import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/alta_proyecto',
      name: 'alta_proyecto',
      component: () => import('../views/ProjectFormView.vue'),
    },
  ],
})

export default router
