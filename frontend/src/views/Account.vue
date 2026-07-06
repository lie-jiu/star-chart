<template>
  <div class="account-page">
    <h1 class="page-title">账号设置</h1>

    <!-- 修改用户名 -->
    <div class="card">
      <h3>修改用户名</h3>
      <form @submit.prevent="changeUsername">
        <div class="form-group">
          <label>当前用户名</label>
          <input class="input" :value="currentUser.username" disabled />
        </div>
        <div class="form-group">
          <label>新用户名</label>
          <input class="input" v-model="usernameForm.new" placeholder="请输入新用户名" required />
        </div>
        <div v-if="usernameError" class="error-msg">{{ usernameError }}</div>
        <div v-if="usernameSuccess" class="success-msg">{{ usernameSuccess }}</div>
        <button type="submit" class="btn btn-primary">修改用户名</button>
      </form>
      <p class="hint">用户名必须是纯英文，至少 3 个字符</p>
    </div>

    <!-- 修改密码 -->
    <div class="card">
      <h3>修改密码</h3>
      <form @submit.prevent="changePassword">
        <div class="form-group">
          <label>旧密码</label>
          <input class="input" type="password" v-model="pwdForm.old" placeholder="请输入旧密码" required />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input class="input" type="password" v-model="pwdForm.new" placeholder="请输入新密码" required />
        </div>
        <div class="form-group">
          <label>确认新密码</label>
          <input class="input" type="password" v-model="pwdForm.confirm" placeholder="请再次输入新密码" required />
        </div>
        <div v-if="pwdError" class="error-msg">{{ pwdError }}</div>
        <div v-if="pwdSuccess" class="success-msg">{{ pwdSuccess }}</div>
        <button type="submit" class="btn btn-primary">修改密码</button>
      </form>
    </div>

    <!-- 注销账号 -->
    <div class="card danger-zone">
      <h3>注销账号</h3>
      <p class="hint">此操作不可恢复，注销后你的所有数据将被永久删除。</p>
      <button class="btn btn-danger" @click="confirmDelete">注销我的账号</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const currentUser = ref({})
const usernameForm = ref({ new: '' })
const pwdForm = ref({ old: '', new: '', confirm: '' })
const usernameError = ref('')
const usernameSuccess = ref('')
const pwdError = ref('')
const pwdSuccess = ref('')

const changeUsername = async () => {
  usernameError.value = ''
  usernameSuccess.value = ''
  if (usernameForm.value.new === currentUser.value.username) {
    usernameError.value = '新用户名和当前用户名相同'
    return
  }
  try {
    await api.patch('/auth/me', { username: usernameForm.value.new })
    usernameSuccess.value = `用户名修改成功：${usernameForm.value.new}`
    currentUser.value.username = usernameForm.value.new
    usernameForm.value.new = ''
  } catch (e) {
    usernameError.value = e.response?.data?.detail || '修改失败'
  }
}

const changePassword = async () => {
  pwdError.value = ''
  pwdSuccess.value = ''
  if (pwdForm.value.new !== pwdForm.value.confirm) {
    pwdError.value = '两次新密码输入不一致'
    return
  }
  try {
    await api.post('/auth/change-password', {
      old_password: pwdForm.value.old,
      new_password: pwdForm.value.new
    })
    pwdSuccess.value = '密码修改成功'
    pwdForm.value = { old: '', new: '', confirm: '' }
  } catch (e) {
    pwdError.value = e.response?.data?.detail || '修改失败'
  }
}

const confirmDelete = () => {
  if (!confirm('确定要注销账号吗？此操作不可恢复！')) return
  deleteAccount()
}

const deleteAccount = async () => {
  try {
    await api.delete('/auth/me')
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    delete api.defaults.headers.common['Authorization']
    window.location.href = '/login'
  } catch (e) {
    alert(e.response?.data?.detail || '删除失败')
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get('/auth/me')
    currentUser.value = data
  } catch (e) {
    console.error(e)
  }
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
  padding: 24px;
  border: 1px solid var(--border);
  margin-bottom: 20px;
}

.card h3 {
  font-size: 16px;
  margin-bottom: 16px;
}

.danger-zone {
  border-color: var(--red);
}

.danger-zone h3 {
  color: var(--red);
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

.input {
  width: 100%;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
}

.input:focus {
  border-color: var(--accent);
}

.btn-primary {
  margin-top: 8px;
  padding: 8px 16px;
  background: var(--accent);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-danger {
  background: var(--red);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.error-msg {
  color: var(--red);
  font-size: 13px;
  margin-bottom: 8px;
}

.success-msg {
  color: var(--green);
  font-size: 13px;
  margin-bottom: 8px;
}

.hint {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 12px;
  line-height: 1.5;
}
</style>
