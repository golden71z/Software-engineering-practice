<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="logo-line">
        <el-icon :size="26" color="#2563eb"><Search /></el-icon>
        <span>校园失物招领</span>
      </div>

      <h2>注册账号</h2>
      <p class="sub">填写基本信息即可开始使用</p>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent>
        <el-form-item prop="username">
          <el-input v-model="form.username" size="large" placeholder="用户名（3-32 位）" :prefix-icon="User" clearable />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" size="large" placeholder="邮箱" :prefix-icon="Message" clearable />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" size="large" placeholder="密码（至少 6 位）" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirm">
          <el-input v-model="form.confirm" type="password" size="large" placeholder="确认密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item prop="real_name">
              <el-input v-model="form.real_name" size="large" placeholder="真实姓名（选填）" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item prop="phone">
              <el-input v-model="form.phone" size="large" placeholder="手机号（选填）" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-button type="primary" size="large" class="submit" :loading="loading" @click="onSubmit">
          注册
        </el-button>
      </el-form>

      <div class="foot">
        已有账号？
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Lock, Message, Search, User } from '@element-plus/icons-vue'
import { register } from '@/api/auth'

const router = useRouter()
const formRef = ref()
const loading = ref(false)

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirm: '',
  real_name: '',
  phone: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 32, message: '长度为 3-32 位', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 64, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
  phone: [
    {
      pattern: /^1[3-9]\d{9}$/,
      message: '手机号格式不正确',
      trigger: 'blur',
    },
  ],
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.warning('请检查标红的输入项')
    return
  }

  loading.value = true
  try {
    await register({
      username: form.username.trim(),
      email: form.email.trim(),
      password: form.password,
      real_name: form.real_name.trim() || null,
      phone: form.phone.trim() || null,
    })
    ElMessage.success('注册成功，请登录')
    router.replace({ path: '/login', query: { username: form.username.trim() } })
  } catch {
    // 拦截器已提示
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
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.08);
}

.logo-line {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--brand);
  font-weight: 600;
  margin-bottom: 20px;
}

h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.sub {
  margin: 0 0 20px;
  color: var(--text-sub);
  font-size: 13px;
}

.submit {
  width: 100%;
}

.foot {
  margin-top: 16px;
  font-size: 13px;
  text-align: center;
  color: var(--text-sub);
}

.foot a {
  color: var(--brand);
  font-weight: 500;
}
</style>
