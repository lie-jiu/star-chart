<template>
  <div class="stocks">
    <h1 class="page-title">美股分析</h1>

    <!-- 搜索 -->
    <div class="search-bar">
      <input
        class="input search-input"
        v-model="searchQuery"
        @keyup.enter="search"
        placeholder="搜索股票代码或名称，例如：AAPL、Tesla"
      />
      <button class="btn btn-primary" @click="search">搜索</button>
    </div>

    <!-- 搜索结果 -->
    <div v-if="searchResults.length > 0" class="card search-results">
      <div v-for="r in searchResults" :key="r.symbol" class="search-item" @click="addWatchlist(r)">
        <div>
          <strong>{{ r.symbol }}</strong>
          <span class="search-name">{{ r.name }}</span>
        </div>
        <span class="badge badge-unknown">{{ r.exchange }}</span>
      </div>
    </div>

    <!-- 关注列表 -->
    <div class="card" style="margin-top: 20px">
      <h3 style="margin-bottom: 16px">关注列表</h3>
      <div v-if="watchlist.length === 0" class="empty">搜索并添加股票到关注列表</div>
      <div v-else class="watchlist">
        <div
          v-for="item in watchlist"
          :key="item.symbol"
          class="watchlist-item"
          @click="selectStock(item)"
          :class="selectedSymbol === item.symbol ? 'selected' : ''"
        >
          <div class="wl-symbol">{{ item.symbol }}</div>
          <div class="wl-name">{{ item.name }}</div>
          <div class="wl-price" v-if="item.quote && !item.quote.error">
            ${{ item.quote.price?.toFixed(2) }}
          </div>
          <div class="wl-change" v-if="item.quote && !item.quote.error"
               :class="item.quote.change >= 0 ? 'positive' : 'negative'">
            {{ item.quote.change >= 0 ? '+' : '' }}{{ item.quote.change_percent?.toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>

    <!-- 详情区 -->
    <div v-if="selectedSymbol" class="card detail-card">
      <div class="detail-header">
        <h2>{{ selectedSymbol }}</h2>
        <div class="range-tabs">
          <button
            v-for="r in ranges"
            :key="r.value"
            class="btn"
            :class="selectedRange === r.value ? 'btn-primary' : ''"
            @click="loadHistory(r.value)"
          >{{ r.label }}</button>
        </div>
      </div>
      <div ref="chartContainer" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import * as echarts from 'echarts'
import api from '../api'

const searchQuery = ref('')
const searchResults = ref([])
const watchlist = ref([])
const selectedSymbol = ref('')
const selectedRange = ref('1mo')
const chartContainer = ref(null)
let chart = null

const ranges = [
  { label: '1天', value: '1d' },
  { label: '5天', value: '5d' },
  { label: '1月', value: '1mo' },
  { label: '3月', value: '3mo' },
  { label: '6月', value: '6mo' },
  { label: '1年', value: '1y' },
  { label: '5年', value: '5y' },
]

const fetchWatchlist = async () => {
  try {
    const { data } = await api.get('/stocks/watchlist')
    watchlist.value = data
  } catch (e) { console.error(e) }
}

const search = async () => {
  if (!searchQuery.value.trim()) return
  try {
    const { data } = await api.get(`/stocks/search?q=${encodeURIComponent(searchQuery.value)}`)
    searchResults.value = data
  } catch (e) { console.error(e) }
}

const addWatchlist = async (item) => {
  try {
    await api.post('/stocks/watchlist', {
      symbol: item.symbol,
      name: item.name
    })
    searchResults.value = []
    searchQuery.value = ''
    fetchWatchlist()
  } catch (e) { console.error(e) }
}

const selectStock = async (item) => {
  selectedSymbol.value = item.symbol
  await loadHistory(selectedRange.value)
}

const loadHistory = async (range) => {
  selectedRange.value = range
  if (!selectedSymbol.value) return
  try {
    const { data } = await api.get(`/stocks/history/${selectedSymbol.value}?range=${range}`)
    if (data.candles) {
      renderChart(data.candles)
    }
  } catch (e) { console.error(e) }
}

const renderChart = (candles) => {
  nextTick(() => {
    if (!chartContainer.value) return
    if (!chart) {
      chart = echarts.init(chartContainer.value, 'dark')
    }

    const dates = candles.map(c => c.date)
    const values = candles.map(c => [c.open, c.close, c.low, c.high])

    chart.setOption({
      backgroundColor: 'transparent',
      animation: false,
      legend: {
        data: ['K线'],
        textStyle: { color: '#9aa0a6' },
        top: 0,
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
      },
      grid: {
        left: '10%',
        right: '10%',
        top: '15%',
        bottom: '15%',
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLine: { lineStyle: { color: '#2d3140' } },
        axisLabel: { color: '#9aa0a6' },
      },
      yAxis: {
        scale: true,
        axisLine: { lineStyle: { color: '#2d3140' } },
        axisLabel: { color: '#9aa0a6' },
        splitLine: { lineStyle: { color: '#2d3140' } },
      },
      dataZoom: [
        { type: 'inside', start: 50, end: 100 },
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: values,
          itemStyle: {
            color: '#00b894',
            color0: '#ff6b6b',
            borderColor: '#00b894',
            borderColor0: '#ff6b6b',
          },
        },
      ],
    })
  })
}

onMounted(() => {
  fetchWatchlist()
  window.addEventListener('resize', () => chart && chart.resize())
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
}

.search-results {
  margin-top: 12px;
}

.search-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-item:hover {
  background: var(--bg-secondary);
}

.search-name {
  color: var(--text-secondary);
  font-size: 13px;
  margin-left: 10px;
}

.watchlist {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 10px;
}

.watchlist-item {
  background: var(--bg-secondary);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.watchlist-item:hover {
  border-color: var(--accent);
}

.watchlist-item.selected {
  border-color: var(--accent);
  background: rgba(108, 92, 231, 0.1);
}

.wl-symbol {
  font-weight: 600;
  font-size: 15px;
}

.wl-name {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.wl-price {
  font-size: 18px;
  font-weight: 700;
  margin-top: 6px;
}

.wl-change {
  font-size: 12px;
  font-weight: 500;
  margin-top: 2px;
}

.positive { color: var(--green); }
.negative { color: var(--red); }

.empty {
  text-align: center;
  padding: 30px;
  color: var(--text-secondary);
}

.detail-card {
  margin-top: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.detail-header h2 {
  font-size: 20px;
}

.range-tabs {
  display: flex;
  gap: 6px;
}

.range-tabs .btn {
  padding: 6px 12px;
  font-size: 12px;
  background: var(--bg-secondary);
  color: var(--text-secondary);
}

.range-tabs .btn-primary {
  background: var(--accent);
  color: white;
}

.chart-container {
  width: 100%;
  height: 450px;
}

@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
  }
  .watchlist {
    grid-template-columns: repeat(2, 1fr);
  }
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  .chart-container {
    height: 300px;
  }
}
</style>
