<template>
  <div class="page-container">
    <h2 class="section-title">我的认领申请</h2>

    <el-card shadow="never" class="card" v-loading="loading">
      <el-table :data="list" stripe>
        <el-table-column label="物品" min-width="240">
          <template #default="{ row }">
            <router-link :to="`/items/${row.item_id}`" class="link">
              {{ row.item_title }}
            </router-link>
            <el-tag size="small" :type="typeTagType(row.item_type)" class="ml">
              {{ TYPE_TEXT[row.item_type] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="proof" label="认领说明" min-width="240" show-overflow-tooltip />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag size="small" :type="claimStatusType(row.status)">
              {{ CLAIM_STATUS_TEXT[row.status] }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="处理意见" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">{{ row.handle_comment || '-' }}</template>
        </el-table-column>
        <el-table-column label="申请时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              link
              type="danger"
              @click="onCancel(row)"
            >
              撤销
            </el-button>
            <span v-else class="text-sub">—</span>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loading && !list.length" description="还没有提交过认领申请">
        <el-button type="primary" @click="router.push('/items')">去看看有哪些失物</el-button>
      </el-empty>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { cancelClaim, listMyClaims } from '@/api/claim'
import {
  CLAIM_STATUS_TEXT,
  TYPE_TEXT,
  claimStatusType,
  formatTime,
  typeTagType,
} from '@/utils/format'

const router = useRouter()
const list = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = (await listMyClaims()) || []
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

async function onCancel(row) {
  await ElMessageBox.confirm('确认撤销这条认领申请？', '提示', { type: 'warning' }).catch(() =>
    Promise.reject(new Error('cancel'))
  )
  try {
    await cancelClaim(row.id)
    ElMessage.success('已撤销')
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

.link {
  color: var(--brand);
}

.ml {
  margin-left: 8px;
}
</style>
