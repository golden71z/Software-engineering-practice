<template>
  <el-card shadow="never" class="card">
    <div class="toolbar">
      <el-radio-group v-model="query.type" @change="reload">
        <el-radio-button :value="''">全部</el-radio-button>
        <el-radio-button value="lost">失物</el-radio-button>
        <el-radio-button value="found">招领</el-radio-button>
      </el-radio-group>

      <el-select v-model="query.status" style="width: 140px" @change="reload">
        <el-option label="全部状态" value="all" />
        <el-option label="寻找中" value="published" />
        <el-option label="已归还" value="returned" />
        <el-option label="已下架" value="offline" />
      </el-select>

      <el-input
        v-model="query.keyword"
        placeholder="搜索标题/描述/地点"
        clearable
        style="width: 240px"
        :prefix-icon="Search"
        @keyup.enter="reload"
        @clear="reload"
      />
      <el-button type="primary" @click="reload">查询</el-button>
    </div>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip>
        <template #default="{ row }">
          <router-link :to="`/items/${row.id}`" class="link">{{ row.title }}</router-link>
        </template>
      </el-table-column>
      <el-table-column label="类型" width="80">
        <template #default="{ row }">
          <el-tag size="small" :type="typeTagType(row.type)">{{ TYPE_TEXT[row.type] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="category_name" label="分类" width="110" />
      <el-table-column prop="publisher_name" label="发布者" width="120" />
      <el-table-column prop="location" label="地点" width="150" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="itemStatusType(row.status)">
            {{ ITEM_STATUS_TEXT[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布时间" width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="110" fixed="right">
        <template #default="{ row }">
          <el-button
            v-if="row.status !== 'offline'"
            link
            type="warning"
            @click="onOffline(row)"
          >
            下架
          </el-button>
          <el-button v-else link type="primary" @click="onRestore(row)">恢复</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!loading && !list.length" description="没有符合条件的信息" />

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
import { listAllItems } from '@/api/admin'
import { offlineItem, restoreItem } from '@/api/item'
import {
  ITEM_STATUS_TEXT,
  TYPE_TEXT,
  formatTime,
  itemStatusType,
  typeTagType,
} from '@/utils/format'

const loading = ref(false)
const list = ref([])
const total = ref(0)

const query = reactive({
  type: '',
  status: 'all',
  keyword: '',
  page: 1,
  size: 10,
})

async function load() {
  loading.value = true
  try {
    const data = await listAllItems({
      type: query.type || undefined,
      status: query.status || 'all',
      keyword: query.keyword || undefined,
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

async function onOffline(row) {
  const confirmed = await ElMessageBox.confirm(
    `确认下架「${row.title}」？下架后前台不再展示，可随时恢复。`,
    '下架信息',
    { type: 'warning', confirmButtonText: '确认下架', cancelButtonText: '取消' }
  ).catch(() => false)
  if (!confirmed) return

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
    ElMessage.success('已恢复展示')
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

.link {
  color: var(--brand);
}

.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
