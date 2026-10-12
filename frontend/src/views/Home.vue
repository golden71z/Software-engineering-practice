<template>
  <div class="home">
    <el-card class="card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="title">校园失物招领管理系统</span>
          <el-tag type="info" size="small">项目骨架验证</el-tag>
        </div>
      </template>

      <div class="content">
        <p class="desc">
          本页面用于验证前后端联通性。点击下方按钮请求后端健康检查接口，
          若能正常返回数据，说明 Vite 代理、跨域配置、Axios 拦截器、
          统一响应体全部工作正常。
        </p>

        <el-button
          type="primary"
          :loading="loading"
          @click="handleCheck"
        >
          测试后端连接
        </el-button>

        <el-alert
          v-if="status === 'success'"
          class="result"
          type="success"
          :closable="false"
          show-icon
        >
          <template #title>{{ resultMessage }}</template>
          <div class="detail">
            <div v-for="(value, key) in resultData" :key="key" class="detail-row">
              <span class="label">{{ key }}</span>
              <span class="value">{{ value }}</span>
            </div>
          </div>
        </el-alert>

        <el-alert
          v-else-if="status === 'error'"
          class="result"
          type="error"
          :closable="false"
          show-icon
          :title="errorMessage"
        >
          <div class="detail">
            <div>请检查后端服务是否已启动（默认端口 8080）。</div>
          </div>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { checkHealth } from '@/api/health'

const loading = ref(false)
const status = ref('')
const resultMessage = ref('')
const resultData = ref({})
const errorMessage = ref('')

const handleCheck = async () => {
  loading.value = true
  status.value = ''
  try {
    const res = await checkHealth()
    resultMessage.value = res.message
    resultData.value = res.data
    status.value = 'success'
  } catch (e) {
    errorMessage.value = e.message || '连接失败'
    status.value = 'error'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 100vh;
  padding: 80px 20px;
}

.card {
  width: 100%;
  max-width: 620px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 17px;
  font-weight: 500;
}

.desc {
  font-size: 14px;
  line-height: 1.8;
  color: #606266;
  margin-bottom: 24px;
}

.result {
  margin-top: 24px;
}

.detail {
  margin-top: 10px;
  font-size: 13px;
  line-height: 2;
}

.detail-row {
  display: flex;
}

.label {
  width: 90px;
  color: #909399;
}

.value {
  color: #303133;
  font-family: Consolas, Monaco, monospace;
}
</style>
