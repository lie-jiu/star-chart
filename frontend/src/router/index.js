import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Monitor from '../views/Monitor.vue'
import Stocks from '../views/Stocks.vue'
import News from '../views/News.vue'
import Login from '../views/Login.vue'

const routes = [
  { path: '/login', name: 'login', component: Login, meta: { public: true } },
  { path: '/', name: 'dashboard', component: Dashboard },
  { path: '/monitor', name: 'monitor', component: Monitor },
  { path: '/stocks', name: 'stocks', component: Stocks },
  { path: '/news', name: 'news', component: News },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (!to.meta.public && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
