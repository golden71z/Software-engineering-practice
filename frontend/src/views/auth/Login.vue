<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="logo-line">
        <el-icon :size="26" color="#2563eb"><Search /></el-icon>
        <span>校园失物招领</span>
      </div>

      <h2>欢迎回来</h2>
      <p class="sub">登录后可以发布信息、申请认领</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            size="large"
            placeholder="用户名"
            :prefix-icon="User"
            clearable
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            size="large"
            placeholder="密码"
            :prefix-icon="Lock"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>

        <el-button
          type="primary"
          size="large"
          class="submit"
          :loading="loading"
          @click="onSubmit"
        >
          登录
        </el-button>
      </el-form>

      <div class="foot">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>

      <div class="demo">
        演示账号：student01 / abc123<br />
        管理员：admin / admin123
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Search, User } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: typeof route.query.username === 'string' ? route.query.username : '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.warning('请检查标红的输入项')
    return
  }

  loading.value = true
  try {
    await user.login({ username: form.username.trim(), password: form.password })
    ElMessage.success(`欢迎回来，${user.displayName}`)
    const redirect = route.query.redirect
    router.replace(typeof redirect === 'string' && redirect ? redirect : '/')
  } catch {
    // 错误提示已由响应拦截器统一弹出
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #eff6ff 0%, #f5f7fa 45%, #ecfdf5 100%);
  padding: 24px;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 36px 32px 28px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
}

.logo-line {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--brand);
  font-weight: 600;
  margin-bottom: 22px;
}

h2 {
  margin: 0 0 6px;
  font-size: 24px;
}

.sub {
  margin: 0 0 24px;
  color: var(--text-sub);
  font-size: 13px;
}

.submit {
  width: 100%;
  margin-top: 4px;
}

.foot {
  margin-top: 18px;
  font-size: 13px;
  text-align: center;
  color: var(--text-sub);
}

.foot a {
  color: var(--brand);
  font-weight: 500;
}

.demo {
  margin-top: 16px;
  padding: 10px 12px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 12px;
  color: #9ca3af;
  line-height: 1.7;
}
</style>
