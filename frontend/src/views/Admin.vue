<template>
  <div class="admin-page">
    <h1 class="page-title">⚙️ 系统管理</h1>

    <!-- 用户管理 -->
    <div class="card">
      <h3>用户管理</h3>
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>用户名</th>
            <th>管理员</th>
            <th>注册时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>
              <strong>{{ user.username }}</strong>
              <span v-if="user.id === currentUserId" class="badge badge-current">我</span>
            </td>
            <td>
              <span v-if="user.is_admin" class="badge badge-admin">管理员</span>
              <span v-else class="badge badge-normal">普通</span>
            </td>
            <td class="time-cell">{{ formatDate(user.created_at) }}</td>
            <td>
              <button
                v-if="user.id !== currentUserId"
                class="btn btn-sm"
                :class="user.is_admin ? 'btn-warning' : 'btn-success'"
                @click="toggleAdmin(user)"
              >
                {{ user.is_admin ? '取消管理员' : '设为管理员' }}
              </button>
              <button
                v-if="user.id !== currentUserId"
                class="btn btn-danger btn-sm"
                @click="deleteUser(user)"
              >
                删除
              </button>
              <span v-else class="text-muted">—</span>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="users.length === 0" class="empty">暂无用户</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import api from '../api'

const users = ref([])
const currentUserId = ref(null)

const fetchUsers = async () => {
  try {
    const { data } = await api.get('/auth/users')
    users.value = data
  } catch (e) {
    console.error(e)
  }
}

const toggleAdmin = async (user) => {
  try {
    if (user.is_admin) {
      await api.post(`/auth/unset-admin/${user.id}`)
    } else {
      await api.post(`/auth/set-admin/${user.id}`)
    }
    fetchUsers()
  } catch (e) {
    alert(e.response?.data?.detail || '操作失败')
  }
}

const deleteUser = async (user) => {
  if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可恢复！`)) return
  try {
    await api.delete(`/auth/delete/${user.id}`)
    fetchUsers()
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

const formatDate = (d) => {
  return d ? dayjs(d).add(8, 'hour').format('YYYY-MM-DD HH:mm') : '-'
}

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me')
    currentUserId.value = data.id
  } catch (e) { console.error(e) }
  fetchUsers()
})
</script>

<style scoped>
.page-title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 24px;
}

.card {
  background: var(--bg-card);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border);
  margin-bottom: 20px;
}

.card h3 {
  font-size: 16px;
  margin-bottom: 16px;
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

.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
  margin-left: 6px;
}

.badge-current {
  background: rgba(108, 92, 231, 0.2);
  color: var(--accent-light);
}

.badge-admin {
  background: rgba(255, 107, 107, 0.2);
  color: var(--red);
}

.badge-normal {
  background: rgba(150, 150, 150, 0.2);
  color: var(--text-secondary);
}

.time-cell {
  font-size: 12px;
  color: var(--text-secondary);
}

.text-muted {
  color: var(--text-secondary);
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-right: 4px;
}

.btn-success {
  background: var(--green);
  color: white;
}

.btn-warning {
  background: var(--yellow);
  color: #333;
}

.btn-danger {
  background: var(--red);
  color: white;
}

.empty {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}
</style>
