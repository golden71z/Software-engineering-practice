<template>
  <el-card shadow="never" class="similar-card" :body-style="{ padding: '14px 18px' }">
    <div class="similar-head">
      <strong>相似招领</strong>
      <span class="text-sub">可能与你的失物有关，请核实后认领</span>
    </div>
    <p v-if="loading" class="hint text-sub">正在查找相似招领…</p>
    <div v-else-if="failed" class="hint text-sub">
      暂时无法加载推荐
      <el-button link type="primary" @click="load">重试</el-button>
    </div>
    <p v-else-if="!rows.length" class="hint text-sub">暂未找到相似招领，有新招领信息后可再次查看。</p>
    <div v-else class="similar-list">
      <router-link v-for="row in rows" :key="row.id" :to="`/items/${row.id}`" class="similar-row">
        <el-image v-if="row.thumbnail" :src="row.thumbnail" fit="cover" class="thumbnail">
          <template #error><el-icon><Picture /></el-icon></template>
        </el-image>
        <div v-else class="thumbnail placeholder"><el-icon><Picture /></el-icon></div>
        <div class="similar-info">
          <div class="similar-title">{{ row.title }}</div>
          <div class="similar-meta">{{ row.location }} · {{ formatTime(row.event_time) }}</div>
          <div class="similar-reasons">{{ row.reasons.join(' · ') }}</div>
        </div>
        <span class="view-detail">查看详情</span>
      </router-link>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Picture } from '@element-plus/icons-vue'
import { getSimilarFound } from '@/api/item'
import { formatTime } from '@/utils/format'

const props = defineProps({ itemId: { type: Number, required: true } })
const rows = ref([])
const loading = ref(false)
const failed = ref(false)
let requestVersion = 0

async function load() {
  const version = ++requestVersion
  rows.value = []
  loading.value = true
  failed.value = false
  try {
    const result = await getSimilarFound(props.itemId)
    if (version === requestVersion) rows.value = (result || []).slice(0, 3)
  } catch {
    if (version === requestVersion) failed.value = true
  } finally {
    if (version === requestVersion) loading.value = false
  }
}

watch(() => props.itemId, load, { immediate: true })
</script>

<style scoped>
.similar-card { margin-top: 16px; border-radius: var(--radius); }
.similar-head { display: flex; align-items: baseline; flex-wrap: wrap; gap: 6px 14px; }
.similar-head strong { font-size: 14px; }
.similar-head span, .hint { font-size: 12px; }
.hint { margin: 10px 0 0; }
.similar-list { margin-top: 8px; }
.similar-row { display: flex; align-items: center; gap: 12px; padding: 9px 0; border-bottom: 1px solid #f1f5f9; }
.similar-row:last-child { border-bottom: 0; padding-bottom: 0; }
.thumbnail { width: 48px; height: 48px; border-radius: 6px; flex-shrink: 0; }
.placeholder { display: flex; align-items: center; justify-content: center; background: #f3f4f6; color: #94a3b8; }
.similar-info { flex: 1; min-width: 0; }
.similar-title { color: var(--brand); font-size: 13px; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.similar-meta { color: var(--text-sub); font-size: 12px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; margin-top: 3px; }
.similar-reasons { color: #64748b; font-size: 11px; margin-top: 3px; }
.view-detail { color: var(--brand); font-size: 12px; white-space: nowrap; }
@media (max-width: 480px) { .view-detail { display: none; } }
</style>
