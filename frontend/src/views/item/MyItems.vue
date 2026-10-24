<template>
  <div class="page-container">
    <div class="head">
      <h2 class="section-title">我的发布</h2>
      <el-button type="primary" :icon="Plus" @click="router.push('/publish')">发布新信息</el-button>
    </div>

    <el-card shadow="never" class="table-card">
      <el-tabs v-model="status" @tab-change="load">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="寻找中" name="published" />
        <el-tab-pane label="已归还" name="returned" />
        <el-tab-pane label="已下架" name="offline" />
      </el-tabs>

      <el-table :data="list" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="220">
          <template #default="{ row }">
            <router-link :to="`/items/${row.id}`" class="link">{{ row.title }}</router-link>
          </template>
        </el-table-column>
        <el-table-column label="类型" width="80">
          <template #default="{ row }">
            <el-tag size="small" :type="typeTagType(row.type)">
              {{ TYPE_TEXT[row.type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_name" label="分类" width="110" />
        <el-table-column prop="location" label="地点" width="150" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="itemStatusType(row.status)">
              {{ ITEM_STATUS_TEXT[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="浏览" width="80" prop="view_count" />
        <el-table-column label="发布时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="230" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="router.push(`/publish?id=${row.id}`)">
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'published'"
              link
              type="success"
              @click="onReturned(row)"
            >
              标记归还
            </el-button>
            <el-button
              v-if="row.status !== 'offline'"
              link
              type="warning"
              @click="onOffline(row)"
            >
              下架
            </el-button>
            <el-button v-else link type="primary" @click="onRestore(row)">上架</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !list.length" description="还没有发布过信息" />

      <div class="pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="size"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { listMyItems, markReturned, offlineItem, restoreItem } from '@/api/item'
import {
  ITEM_STATUS_TEXT,
  TYPE_TEXT,
  formatTime,
  itemStatusType,
  typeTagType,
} from '@/utils/format'

const router = useRouter()
const status = ref('all')
const list = ref([])
const total = ref(0)
const page = ref(1)
const size = ref(10)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await listMyItems({
      status: status.value === 'all' ? undefined : status.value,
      page: page.value,
      size: size.value,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

async function onReturned(row) {
  await ElMessageBox.confirm('确认该物品已归还？标记后不可再编辑。', '提示', {
    type: 'warning',
  }).catch(() => Promise.reject(new Error('cancel')))
  try {
    await markReturned(row.id)
    ElMessage.success('已标记归还')
    load()
  } catch {
    /* 已提示 */
  }
}

async function onOffline(row) {
  await ElMessageBox.confirm('下架后其他同学将看不到这条信息，确认？', '提示', {
    type: 'warning',
  }).catch(() => Promise.reject(new Error('cancel')))
  try {
    await offlineItem(row.id)
    ElMessage.success('已下架')
    load()
  } catch {
    /* 已提示 */
  }
}

async function onRestore(row) {
  try {
    await restoreItem(row.id)
    ElMessage.success('已重新上架')
    load()
  } catch {
    /* 已提示 */
  }
}

onMounted(load)
</script>

<style scoped>
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-card {
  border-radius: var(--radius);
}

.link {
  color: var(--brand);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
