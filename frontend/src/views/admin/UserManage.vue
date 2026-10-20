<template>
  <el-card shadow="never" class="card">
    <div class="toolbar">
      <el-input
        v-model="query.keyword"
        placeholder="搜索用户名 / 邮箱 / 姓名"
        clearable
        style="width: 260px"
        :prefix-icon="Search"
        @keyup.enter="reload"
        @clear="reload"
      />
      <el-select v-model="query.role" style="width: 140px" @change="reload">
        <el-option label="全部角色" value="" />
        <el-option label="普通用户" value="user" />
        <el-option label="管理员" value="admin" />
      </el-select>
      <el-button type="primary" @click="reload">查询</el-button>
    </div>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="real_name" label="姓名" width="110">
        <template #default="{ row }">{{ row.real_name || '-' }}</template>
      </el-table-column>
      <el-table-column prop="email" label="邮箱" min-width="200" show-overflow-tooltip />
      <el-table-column prop="phone" label="手机号" width="130">
        <template #default="{ row }">{{ row.phone || '-' }}</template>
      </el-table-column>
      <el-table-column label="角色" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.role === 'admin' ? 'danger' : 'info'">
            {{ row.role === 'admin' ? '管理员' : '普通用户' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="row.status === 1 ? 'success' : 'danger'">
            {{ row.status === 1 ? '正常' : '已禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="注册时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.role !== 'admin'"
            link
            :type="row.status === 1 ? 'danger' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 1 ? '禁用' : '启用' }}
          </el-button>
          <span v-else class="text-sub">—</span>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && !list.length" description="没有找到用户" />

    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="reload"
      />
    </div>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { listUsers, setUserStatus } from '@/api/admin'
import { formatTime } from '@/utils/format'

const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({ keyword: '', role: '', page: 1, size: 10 })

async function load() {
  loading.value = true
  try {
    const data = await listUsers({
      keyword: query.keyword || undefined,
      role: query.role || undefined,
      page: query.page,
      size: query.size,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

function reload() {
  query.page = 1
  load()
}

async function toggleStatus(row) {
  const next = row.status === 1 ? 0 : 1
  const confirmed = await ElMessageBox.confirm(
    next === 0
      ? `确认禁用「${row.username}」？禁用后该用户无法登录。`
      : `确认启用「${row.username}」？`,
    '修改账号状态',
    { type: 'warning' }
  ).catch(() => false)
  if (!confirmed) return

  try {
    await setUserStatus(row.id, next)
    ElMessage.success(next === 1 ? '已启用' : '已禁用')
    load()
  } catch {
    /* 已提示 */
  }
}

onMounted(load)
</script>

<style scoped>
.card {
  border-radius: var(--radius);
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
