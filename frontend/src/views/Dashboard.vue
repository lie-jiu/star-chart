<template>
  <div class="dashboard">
    <h1 class="page-title">总览</h1>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">🖥️</div>
        <div class="stat-info">
          <div class="stat-value">{{ monitorStats.total || 0 }}</div>
          <div class="stat-label">监控目标</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">✅</div>
        <div class="stat-info">
          <div class="stat-value" style="color: var(--green)">{{ monitorStats.up || 0 }}</div>
          <div class="stat-label">正常运行</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">❌</div>
        <div class="stat-info">
          <div class="stat-value" style="color: var(--red)">{{ monitorStats.down || 0 }}</div>
          <div class="stat-label">服务异常</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-info">
          <div class="stat-value">{{ monitorStats.availability || 0 }}%</div>
          <div class="stat-label">可用率</div>
        </div>
      </div>
    </div>

    <!-- 股票关注 -->
    <div class="card" style="margin-top: 24px">
      <h3 style="margin-bottom: 16px">📈 关注股票</h3>
      <div v-if="watchlist.length === 0" class="empty">暂无关注股票，去 <router-link to="/stocks">美股分析</router-link> 添加</div>
      <div v-else class="stock-grid">
        <div v-for="item in watchlist" :key="item.symbol" class="stock-item">
          <div class="stock-symbol">{{ item.symbol }}</div>
          <div class="stock-name">{{ item.name }}</div>
          <div class="stock-price" v-if="item.quote && !item.quote.error">
            ${{ item.quote.price?.toFixed(2) }}
          </div>
          <div class="stock-change" v-if="item.quote && !item.quote.error"
               :class="item.quote.change >= 0 ? 'positive' : 'negative'">
            {{ item.quote.change >= 0 ? '+' : '' }}{{ item.quote.change_percent?.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 最新新闻 -->
    <div class="card" style="margin-top: 24px">
      <h3 style="margin-bottom: 16px">🌍 最新资讯</h3>
      <div v-if="news.length === 0" class="empty">加载中...</div>
      <div v-else class="news-list">
        <a v-for="(item, i) in news.slice(0, 5)" :key="i" :href="item.url" target="_blank" class="news-item">
          <div class="news-title">{{ item.title }}</div>
          <div class="news-meta">{{ item.source }}</div>
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const monitorStats = ref({})
const watchlist = ref([])
const news = ref([])

onMounted(async () => {
  try {
    const { data } = await api.get('/monitor/stats')
    monitorStats.value = data
  } catch (e) { console.error(e) }

  try {
    const { data } = await api.get('/stocks/watchlist')
    watchlist.value = data
  } catch (e) { console.error(e) }

  try {
    const { data } = await api.get('/news/?category=world&limit=5')
    news.value = data
  } catch (e) { console.error(e) }
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  font-size: 32px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.empty {
  color: var(--text-secondary);
  text-align: center;
  padding: 20px;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.stock-item {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 14px;
  text-align: center;
}

.stock-symbol {
  font-weight: 600;
  font-size: 16px;
}

.stock-name {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.stock-price {
  font-size: 20px;
  font-weight: 700;
  margin-top: 8px;
}

.stock-change {
  font-size: 13px;
  margin-top: 4px;
  font-weight: 500;
}

.positive { color: var(--green); }
.negative { color: var(--red); }

.news-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.news-item {
  display: block;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.2s;
}

.news-item:hover {
  background: var(--border);
}

.news-title {
  font-size: 14px;
  line-height: 1.4;
}

.news-meta {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 6px;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .stock-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
