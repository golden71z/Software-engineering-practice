<template>
  <div class="page-container">
    <div class="head">
      <h2 class="section-title">收到的认领申请</h2>
      <el-radio-group v-model="status" @change="load">
        <el-radio-button :value="''">全部</el-radio-button>
        <el-radio-button value="pending">待处理</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已拒绝</el-radio-button>
      </el-radio-group>
    </div>

    <el-alert
      type="warning"
      :closable="false"
      show-icon
      title="通过某条申请后，该物品会自动标记为「已归还」，同物品的其他申请将被自动拒绝。"
      class="tip"
    />

    <el-card shadow="never" class="card" v-loading="loading">
      <div v-for="row in list" :key="row.id" class="claim-item">
        <div class="row-head">
          <div class="item-title">
            <el-tag size="small" :type="typeTagType(row.item_type)">
              {{ TYPE_TEXT[row.item_type] }}
            </el-tag>
            <router-link :to="`/items/${row.item_id}`" class="link">
              {{ row.item_title }}
            </router-link>
          </div>
          <el-tag size="small" :type="claimStatusType(row.status)">
            {{ CLAIM_STATUS_TEXT[row.status] }}
          </el-tag>
        </div>

        <div class="proof">
          <span class="label">认领说明</span>
          <p>{{ row.proof }}</p>
        </div>

        <div class="row-meta">
          <span>申请人：{{ row.applicant_name }}</span>
          <span>联系方式：{{ row.contact || '未填写' }}</span>
          <span>申请时间：{{ formatTime(row.created_at) }}</span>
          <span v-if="row.handle_comment">处理意见：{{ row.handle_comment }}</span>
        </div>

        <div v-if="row.status === 'pending'" class="row-actions">
          <el-button type="success" size="small" @click="onApprove(row)">通过</el-button>
          <el-button type="danger" size="small" plain @click="onReject(row)">拒绝</el-button>
        </div>
      </div>

      <el-empty v-if="!loading && !list.length" description="还没有收到认领申请" />
    </el-card>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { approveClaim, listReceivedClaims, rejectClaim } from '@/api/claim'
import {
  CLAIM_STATUS_TEXT,
  TYPE_TEXT,
  claimStatusType,
  formatTime,
  typeTagType,
} from '@/utils/format'

const list = ref([])
const status = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    list.value = (await listReceivedClaims(status.value || undefined)) || []
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

async function onApprove(row) {
  const { value } = await ElMessageBox.prompt(
    '通过后该物品将标记为已归还，其他申请会被自动拒绝。可填写处理说明：',
    '确认通过认领',
    {
      confirmButtonText: '确认通过',
      cancelButtonText: '取消',
      inputPlaceholder: '例如：已当面核对并交接',
      inputValue: '信息核对无误，已当面交接',
    }
  ).catch(() => ({ value: null }))
  if (value === null) return

  try {
    await approveClaim(row.id, value || null)
    ElMessage.success('已通过，物品标记为已归还')
    load()
  } catch {
    /* 已提示 */
  }
}

async function onReject(row) {
  const { value } = await ElMessageBox.prompt('请填写拒绝原因：', '拒绝认领', {
    confirmButtonText: '确认拒绝',
    cancelButtonText: '取消',
    inputPlaceholder: '例如：描述与物品实际特征不符',
  }).catch(() => ({ value: null }))
  if (value === null) return

  try {
    await rejectClaim(row.id, value || null)
    ElMessage.success('已拒绝')
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
  flex-wrap: wrap;
  gap: 12px;
}

.tip {
  margin-bottom: 16px;
  border-radius: var(--radius);
}

.card {
  border-radius: var(--radius);
}

.claim-item {
  padding: 16px 4px;
  border-bottom: 1px solid #f1f5f9;
}

.claim-item:last-child {
  border-bottom: none;
}

.row-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.item-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.link {
  color: var(--brand);
}

.proof {
  background: #f9fafb;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 10px;
}

.proof .label {
  font-size: 12px;
  color: var(--text-sub);
}

.proof p {
  margin: 4px 0 0;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
}

.row-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  font-size: 12px;
  color: var(--text-sub);
}

.row-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}
</style>
