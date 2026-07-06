<template>
  <div class="auth-layout">
    <div class="auth-box">
      <div class="logo">
        <span class="logo-icon">🗺️</span>
        <span class="logo-text">星图</span>
      </div>
      <h2>{{ isLogin ? '登录' : '注册' }}</h2>

      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label>用户名</label>
          <input class="input" v-model="form.username" placeholder="请输入用户名" required />
        </div>
        <div class="form-group">
          <label>密码</label>
          <input class="input" type="password" v-model="form.password" placeholder="请输入密码" required />
        </div>
        <div class="form-group" v-if="!isLogin">
          <label>确认密码</label>
          <input class="input" type="password" v-model="form.passwordConfirm" placeholder="请再次输入密码" required />
        </div>
        <div v-if="error" class="error-msg">{{ error }}</div>
        <button type="submit" class="btn btn-primary btn-block">{{ isLogin ? '登录' : '注册' }}</button>
      </form>

      <div v-if="!isLogin" class="password-rules">
        <p>用户名要求：纯英文，至少 3 个字符</p>
        <p>密码要求：至少 8 位，含大小写字母、数字、特殊字符</p>
      </div>

      <p class="switch-text">
        {{ isLogin ? '还没有账号？' : '已有账号？' }}
        <a href="#" @click.prevent="isLogin = !isLogin">{{ isLogin ? '注册' : '登录' }}</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '../api'

const router = useRouter()
const isLogin = ref(true)
const form = ref({ username: '', password: '', passwordConfirm: '' })
const error = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
    try {
      const { data } = await api.get('/auth/check')
      if (data.authenticated) {
        router.push('/')
        return
      }
    } catch (e) {
      localStorage.removeItem('token')
      delete api.defaults.headers.common['Authorization']
    }
  }
})

const handleSubmit = async () => {
  error.value = ''
  try {
    if (isLogin.value) {
      const params = new URLSearchParams()
      params.append('username', form.value.username)
      params.append('password', form.value.password)
      const { data } = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      })
      saveAuth(data)
    } else {
      if (form.value.password !== form.value.passwordConfirm) {
        error.value = '两次密码输入不一致'
        return
      }
      const { data } = await api.post('/auth/register', {
        username: form.value.username,
        password: form.value.password
      })
      saveAuth(data)
    }
  } catch (e) {
    error.value = e.response?.data?.detail || '操作失败，请重试'
  }
}

const saveAuth = (data) => {
  localStorage.setItem('token', data.access_token)
  localStorage.setItem('user', JSON.stringify(data.user))
  api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
  router.push('/')
}
</script>

<style scoped>
.auth-layout {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #0f1117 0%, #1a1d27 100%);
  padding: 20px;
}

.auth-box {
  width: 100%;
  max-width: 380px;
  background: var(--bg-card);
  border-radius: 16px;
  padding: 40px 32px;
  border: 1px solid var(--border);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}

.logo-icon {
  font-size: 36px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--accent), var(--accent-light));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

h2 {
  text-align: center;
  margin-bottom: 24px;
  font-size: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.btn-block {
  width: 100%;
  margin-top: 8px;
}

.error-msg {
  color: var(--red);
  font-size: 13px;
  margin-bottom: 8px;
}

.switch-text {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: var(--text-secondary);
}

.switch-text a {
  color: var(--accent-light);
  text-decoration: none;
}

.password-rules {
  margin-top: 16px;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.password-rules p {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.password-rules p::before {
  content: "▸ ";
  color: var(--accent-light);
}
</style>
