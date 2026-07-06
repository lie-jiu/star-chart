<template>
  <div class="layout">
    <!-- 移动端菜单按钮 -->
    <button v-if="isLoggedIn" class="menu-btn" @click="showMobileMenu = !showMobileMenu">☰</button>

    <!-- 侧边栏 -->
    <aside v-if="isLoggedIn" class="sidebar" :class="{ 'sidebar-open': showMobileMenu }" @click.self="showMobileMenu = false">
      <div class="logo">
        <span class="logo-icon">🗺️</span>
        <span class="logo-text">星图</span>
      </div>
      <nav class="nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          active-class="nav-active"
          @click="showMobileMenu = false"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <span>v1.0.0</span>
        <button class="logout-btn" @click="logout">退出登录</button>
      </div>
    </aside>

    <!-- 遮罩层 -->
    <div class="overlay" v-if="showMobileMenu && isLoggedIn" @click="showMobileMenu = false"></div>

    <main class="main" :class="{ 'main-mobile': isMobile }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from './api'

const router = useRouter()
const route = useRoute()
const isMobile = ref(false)
const showMobileMenu = ref(false)

const isLoggedIn = computed(() => {
  return localStorage.getItem('token') !== null && route.name !== 'login'
})

const navItems = [
  { path: '/', name: '总览', icon: '📊' },
  { path: '/monitor', name: '服务监控', icon: '🖥️' },
  { path: '/stocks', name: '美股分析', icon: '📈' },
  { path: '/news', name: '全球新闻', icon: '🌍' },
]

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    showMobileMenu.value = false
  }
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
  delete api.defaults.headers.common['Authorization']
  router.push('/login')
}
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 220px;
  background: var(--bg-secondary);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), var(--accent-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.nav {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  border-radius: 8px;
  color: var(--text-secondary);
  text-decoration: none;
  font-size: 14px;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--bg-card);
  color: var(--text-primary);
}

.nav-active {
  background: var(--accent);
  color: white !important;
}

.nav-icon {
  font-size: 18px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 12px;
  text-align: center;
}

.logout-btn {
  display: block;
  width: 100%;
  margin-top: 8px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--red);
  color: white;
  border-color: var(--red);
}

.main {
  flex: 1;
  margin-left: 220px;
  padding: 24px;
  max-width: 1400px;
}

/* ===== 移动端适配 ===== */
.menu-btn {
  display: none;
  position: fixed;
  top: 12px;
  left: 12px;
  z-index: 99;
  background: var(--bg-card);
  border: 1px solid var(--border);
  color: var(--text-primary);
  font-size: 20px;
  cursor: pointer;
  padding: 8px 10px;
  border-radius: 8px;
}

.overlay {
  display: none;
}

@media (max-width: 768px) {
  .menu-btn {
    display: block;
  }

  .sidebar {
    position: fixed;
    top: 0;
    left: -260px;
    width: 240px;
    z-index: 200;
    transition: left 0.3s ease;
  }

  .sidebar-open {
    left: 0;
  }

  .overlay {
    display: block;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    z-index: 150;
  }

  .main-mobile {
    margin-left: 0;
    padding: 16px;
  }
}
</style>
