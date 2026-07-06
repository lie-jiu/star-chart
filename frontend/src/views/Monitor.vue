<template>
  <div class="monitor">
    <div class="page-header">
      <h1 class="page-title">服务监控</h1>
      <button class="btn btn-primary" @click="showAddModal = true">+ 添加目标</button>
    </div>

    <!-- 统计 -->
    <div class="stats-row">
      <div class="stat-box">
        <span class="stat-num">{{ stats.total || 0 }}</span>
        <span class="stat-lbl">总数</span>
      </div>
      <div class="stat-box">
        <span class="stat-num" style="color: var(--green)">{{ stats.up || 0 }}</span>
        <span class="stat-lbl">正常</span>
      </div>
      <div class="stat-box">
        <span class="stat-num" style="color: var(--red)">{{ stats.down || 0 }}</span>
        <span class="stat-lbl">异常</span>
      </div>
      <div class="stat-box">
        <span class="stat-num">{{ stats.availability || 0 }}%</span>
        <span class="stat-lbl">可用率</span>
      </div>
    </div>

    <!-- 目标列表 -->
    <div class="card" style="margin-top: 20px">
      <table class="table">
        <thead>
          <tr>
            <th>名称</th>
            <th>地址</th>
            <th>类型</th>
            <th>状态</th>
            <th>响应时间</th>
            <th>可用率</th>
            <th>最后检查</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="t in targets" :key="t.id">
            <td><strong>{{ t.name }}</strong></td>
            <td class="url-cell">{{ t.url }}</td>
            <td><span class="badge badge-unknown">{{ t.type }}</span></td>
            <td>
              <span class="badge" :class="`badge-${t.status}`">
                {{ t.status === 'up' ? '✓ 正常' : t.status === 'down' ? '✗ 异常' : '?' }}
              </span>
            </td>
            <td>{{ t.response_time }}ms</td>
            <td>{{ t.uptime }}%</td>
            <td class="time-cell">{{ formatTime(t.last_check) }}</td>
            <td>
              <button class="btn btn-danger" style="padding: 4px 10px; font-size: 12px" @click="deleteTarget(t.id)">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="targets.length === 0" class="empty">暂无监控目标</div>
    </div>

    <!-- 添加弹窗 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
      <div class="modal">
        <h3>添加监控目标</h3>
        <div class="form-group">
          <label>名称</label>
          <input class="input" v-model="form.name" placeholder="例如：Google DNS" />
        </div>
        <div class="form-group">
          <label>URL</label>
          <input class="input" v-model="form.url" placeholder="https://example.com" />
        </div>
        <div class="form-group">
          <label>类型</label>
          <select class="input" v-model="form.type">
            <option value="http">HTTP</option>
            <option value="ping">Ping</option>
            <option value="tcp">TCP Port</option>
          </select>
        </div>
        <div class="form-group">
          <label>检查间隔（秒）</label>
          <input class="input" type="number" v-model.number="form.interval" />
        </div>
        <div class="modal-actions">
          <button class="btn" @click="showAddModal = false">取消</button>
          <button class="btn btn-primary" @click="addTarget">添加</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import dayjs from 'dayjs'

const targets = ref([])
const stats = ref({})
const showAddModal = ref(false)
const form = ref({ name: '', url: '', type: 'http', interval: 60 })

const fetchData = async () => {
  try {
    const { data } = await api.get('/monitor/targets')
    targets.value = data
  } catch (e) { console.error(e) }
  try {
    const { data } = await api.get('/monitor/stats')
    stats.value = data
  } catch (e) { console.error(e) }
}

const addTarget = async () => {
  try {
    await api.post('/monitor/targets', form.value)
    showAddModal.value = false
    form.value = { name: '', url: '', type: 'http', interval: 60 }
    fetchData()
  } catch (e) { console.error(e) }
}

const deleteTarget = async (id) => {
  if (!confirm('确定删除？')) return
  try {
    await api.delete(`/monitor/targets/${id}`)
    fetchData()
  } catch (e) { console.error(e) }
}

const formatTime = (t) => {
  return t ? dayjs(t).add(8, 'hour').format('MM-DD HH:mm:ss') : '-'
}

onMounted(fetchData)
setInterval(fetchData, 30000)
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

.stats-row {
  display: flex;
  gap: 16px;
}

.stat-box {
  flex: 1;
  background: var(--bg-card);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 24px;
  font-weight: 700;
}

.stat-lbl {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid var(--border);
  font-size: 14px;
}

.url-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
}

.time-cell {
  font-size: 12px;
  color: var(--text-secondary);
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal {
  background: var(--bg-card);
  border-radius: 16px;
  padding: 24px;
  width: 420px;
  border: 1px solid var(--border);
}

.modal h3 {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 14px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .stats-row {
    flex-wrap: wrap;
  }
  .stat-box {
    min-width: 80px;
    flex: 1 1 40%;
  }
  .table {
    display: block;
    overflow-x: auto;
    white-space: nowrap;
  }
}
</style>
