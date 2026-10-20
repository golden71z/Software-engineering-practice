<template>
  <el-container class="admin-layout">
    <el-aside width="210px" class="aside">
      <div class="logo">
        <el-icon :size="20"><Setting /></el-icon>
        <span>管理后台</span>
      </div>
      <el-menu :default-active="route.path" router class="menu">
        <el-menu-item index="/admin">
          <el-icon><DataLine /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item index="/admin/items">
          <el-icon><Document /></el-icon>
          <span>内容管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Files /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/notices">
          <el-icon><Bell /></el-icon>
          <span>公告管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="crumb">
          <el-tag type="info" size="small">管理员</el-tag>
          <span>{{ route.meta.title }}</span>
        </div>
        <div class="header-actions">
          <el-button text :icon="HomeFilled" @click="router.push('/')">返回前台</el-button>
          <el-button text type="danger" @click="onLogout">退出</el-button>
        </div>
      </el-header>

      <el-main class="content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router'
import {
  Bell,
  DataLine,
  Document,
  Files,
  HomeFilled,
  Setting,
  User,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

function onLogout() {
  user.logout()
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
}

.aside {
  background: #1f2937;
  border-right: none;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 20px;
  color: #fff;
  font-weight: 600;
  font-size: 16px;
}

.menu {
  border-right: none;
  background: transparent;
}

.menu :deep(.el-menu-item) {
  color: #cbd5e1;
}

.menu :deep(.el-menu-item:hover) {
  background: #374151;
  color: #fff;
}

.menu :deep(.el-menu-item.is-active) {
  background: var(--brand);
  color: #fff;
}

.header {
  height: 60px;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.crumb {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 500;
}

.content {
  background: var(--page-bg);
  padding: 20px;
}
</style>
