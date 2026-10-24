<template>
  <div class="user-layout">
    <header class="topbar">
      <div class="topbar-inner">
        <router-link to="/" class="brand">
          <el-icon :size="22"><Search /></el-icon>
          <span>校园失物招领</span>
        </router-link>

        <nav class="nav">
          <router-link to="/" class="nav-link" :class="{ active: route.path === '/' }">
            首页
          </router-link>
          <router-link
            to="/items"
            class="nav-link"
            :class="{ active: route.path.startsWith('/items') }"
          >
            失物招领
          </router-link>
        </nav>

        <div class="actions">
          <el-button type="primary" :icon="Plus" @click="goPublish">发布信息</el-button>

          <template v-if="user.isLogin">
            <el-dropdown trigger="click" @command="onCommand">
              <span class="user-chip">
                <el-avatar :size="28">{{ user.displayName.slice(0, 1) }}</el-avatar>
                <span class="user-name">{{ user.displayName }}</span>
                <el-icon><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="my-items">我的发布</el-dropdown-item>
                  <el-dropdown-item command="my-claims">我的认领</el-dropdown-item>
                  <el-dropdown-item command="received">
                    收到的申请
                    <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge" />
                  </el-dropdown-item>
                  <el-dropdown-item v-if="user.isAdmin" command="admin" divided>
                    管理后台
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <el-button text @click="router.push('/login')">登录</el-button>
            <el-button @click="router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </header>

    <main class="main">
      <router-view />
    </main>

    <footer class="footer">
      校园失物招领管理系统 · 软件体系结构课程设计
    </footer>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { ArrowDown, Plus, Search } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getPendingCount } from '@/api/claim'

const route = useRoute()
const router = useRouter()
const user = useUserStore()
const pendingCount = ref(0)

async function loadPending() {
  if (!user.isLogin) {
    pendingCount.value = 0
    return
  }
  try {
    pendingCount.value = await getPendingCount()
  } catch {
    pendingCount.value = 0
  }
}

function goPublish() {
  if (!user.isLogin) {
    ElMessageBox.confirm('发布信息需要先登录，是否前往登录？', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '再逛逛',
      type: 'warning',
    })
      .then(() => router.push({ path: '/login', query: { redirect: '/publish' } }))
      .catch(() => {})
    return
  }
  router.push('/publish')
}

function onCommand(command) {
  if (command === 'logout') {
    user.logout()
    pendingCount.value = 0
    router.push('/')
    return
  }
  const map = {
    'my-items': '/my/items',
    'my-claims': '/my/claims',
    received: '/my/received',
    admin: '/admin',
  }
  if (map[command]) router.push(map[command])
}

onMounted(loadPending)
watch(() => route.fullPath, loadPending)
</script>

<style scoped>
.user-layout {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.topbar {
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 100;
}

.topbar-inner {
  max-width: 1180px;
  margin: 0 auto;
  height: 60px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  gap: 32px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 17px;
  font-weight: 600;
  color: var(--brand);
  white-space: nowrap;
}

.nav {
  display: flex;
  gap: 6px;
  flex: 1;
}

.nav-link {
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 14px;
  color: #4b5563;
}

.nav-link:hover {
  background: #f3f4f6;
}

.nav-link.active {
  color: var(--brand);
  background: var(--brand-light);
  font-weight: 500;
}

.actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  outline: none;
}

.user-chip:hover {
  background: #f3f4f6;
}

.user-name {
  font-size: 14px;
  max-width: 90px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.badge {
  margin-left: 6px;
}

.main {
  flex: 1;
}

.footer {
  text-align: center;
  padding: 20px;
  color: #9ca3af;
  font-size: 12px;
  border-top: 1px solid #e5e7eb;
  background: #fff;
}
</style>
