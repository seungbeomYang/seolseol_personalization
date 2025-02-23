import { createRouter, createWebHistory } from 'vue-router';
import Admin from "@/views/Admin.vue"


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Admin
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    },

  ]
})

export default router

