<template>
  <div class="news-page">
    <div class="page-header">
      <h1 class="page-title">全球新闻</h1>
      <button class="btn btn-primary" @click="refresh">🔄 刷新</button>
    </div>

    <!-- 分类标签 -->
    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.id"
        class="btn tab-btn"
        :class="currentCategory === cat.id ? 'btn-primary' : ''"
        @click="switchCategory(cat.id)"
      >{{ cat.name }}</button>
    </div>

    <!-- 新闻列表 -->
    <div class="news-container">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="news.length === 0" class="empty">暂无新闻</div>
      <a
        v-for="(item, i) in news"
        :key="i"
        :href="item.url"
        target="_blank"
        class="news-card"
      >
        <div class="news-content">
          <h3 class="news-title">{{ item.title }}</h3>
          <p class="news-summary">{{ item.summary }}</p>
          <div class="news-footer">
            <span class="news-source">{{ item.source }}</span>
            <span class="news-time">{{ formatTime(item.published_at) }}</span>
          </div>
        </div>
      </a>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import dayjs from 'dayjs'

const categories = ref([])
const currentCategory = ref('world')
const news = ref([])
const loading = ref(false)

const fetchCategories = async () => {
  try {
    const { data } = await api.get('/news/categories')
    categories.value = data.categories
  } catch (e) { console.error(e) }
}

const fetchNews = async () => {
  loading.value = true
  try {
    const { data } = await api.get(`/news/?category=${currentCategory.value}&limit=30`)
    news.value = data
  } catch (e) { console.error(e) }
  loading.value = false
}

const switchCategory = (id) => {
  currentCategory.value = id
  fetchNews()
}

const refresh = async () => {
  try {
    await api.post('/news/refresh')
    fetchNews()
  } catch (e) { console.error(e) }
}

const formatTime = (t) => {
  if (!t) return ''
  const d = dayjs(t)
  const now = dayjs()
  if (now.diff(d, 'hour') < 1) return `${now.diff(d, 'minute')} 分钟前`
  if (now.diff(d, 'hour') < 24) return `${now.diff(d, 'hour')} 小时前`
  return d.format('MM-DD HH:mm')
}

onMounted(() => {
  fetchCategories()
  fetchNews()
})
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
}

.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.tab-btn {
  background: var(--bg-card);
  color: var(--text-secondary);
  padding: 8px 16px;
  font-size: 13px;
}

.tab-btn.btn-primary {
  background: var(--accent);
  color: white;
}

.news-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-card {
  display: block;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 18px;
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
}

.news-card:hover {
  border-color: var(--accent);
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(108, 92, 231, 0.15);
}

.news-title {
  font-size: 16px;
  font-weight: 600;
  line-height: 1.5;
  margin-bottom: 8px;
}

.news-summary {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-secondary);
}

.news-source {
  color: var(--accent-light);
  font-weight: 500;
}

.loading, .empty {
  text-align: center;
  padding: 60px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .category-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 4px;
  }
  .tab-btn {
    white-space: nowrap;
  }
}
</style>
