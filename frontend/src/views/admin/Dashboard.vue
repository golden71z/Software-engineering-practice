<template>
  <div v-loading="loading">
    <div class="stat-grid">
      <el-card v-for="s in statCards" :key="s.label" shadow="never" class="stat-card">
        <div class="stat-label">{{ s.label }}</div>
        <div class="stat-value" :style="{ color: s.color }">
          {{ s.value }}<span class="unit">{{ s.unit }}</span>
        </div>
        <div class="stat-hint">{{ s.hint }}</div>
      </el-card>
    </div>

    <el-row :gutter="16" class="mt-16">
      <el-col :span="14">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-title">分类分布</div>
          </template>
          <div ref="pieRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="never" class="chart-card">
          <template #header>
            <div class="card-title">失物 / 招领占比</div>
          </template>
          <div ref="typeRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="mt-16 rate-card">
      <div class="rate-block">
        <div class="rate-label">归还率</div>
        <el-progress
          type="dashboard"
          :percentage="Number(stats.return_rate || 0)"
          :width="120"
          :color="progressColor"
        />
        <div class="rate-hint">
          已归还 {{ stats.returned || 0 }} 条 / 共 {{ stats.total || 0 }} 条
        </div>
      </div>

      <el-divider direction="vertical" class="divider" />

      <div class="rate-block">
        <div class="rate-label">平均归还耗时</div>
        <div class="big-number">{{ stats.avg_return_hours || 0 }}<span class="unit">小时</span></div>
        <div class="rate-hint">从发布到标记归还的平均时长</div>
      </div>

      <el-divider direction="vertical" class="divider" />

      <div class="rate-block">
        <div class="rate-label">待处理认领</div>
        <div class="big-number">{{ stats.pending_claims || 0 }}<span class="unit">条</span></div>
        <div class="rate-hint">全站处于待处理状态的申请</div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'
import { getDashboard } from '@/api/admin'

const loading = ref(false)
const stats = ref({})
const pieRef = ref()
const typeRef = ref()

let pieChart = null
let typeChart = null

const statCards = computed(() => [
  {
    label: '信息总量',
    value: stats.value.total || 0,
    unit: ' 条',
    hint: `其中展示中 ${stats.value.published || 0} 条`,
    color: '#2563eb',
  },
  {
    label: '失物信息',
    value: stats.value.lost || 0,
    unit: ' 条',
    hint: '同学丢失的物品',
    color: '#dc2626',
  },
  {
    label: '招领信息',
    value: stats.value.found || 0,
    unit: ' 条',
    hint: '好心人捡到的物品',
    color: '#059669',
  },
  {
    label: '注册用户',
    value: stats.value.user_count || 0,
    unit: ' 人',
    hint: `已下架 ${stats.value.offline || 0} 条`,
    color: '#7c3aed',
  },
])

const progressColor = [
  { color: '#f56c6c', percentage: 40 },
  { color: '#e6a23c', percentage: 70 },
  { color: '#67c23a', percentage: 100 },
]

function renderCharts() {
  const distribution = stats.value.category_distribution || []
  const typeDistribution = stats.value.type_distribution || []

  pieChart = echarts.init(pieRef.value)
  pieChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 条 ({d}%)' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    series: [
      {
        type: 'pie',
        radius: ['42%', '68%'],
        center: ['50%', '44%'],
        avoidLabelOverlap: true,
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b}\n{c}' },
        data: distribution.map((d) => ({ name: d.name, value: d.value })),
      },
    ],
  })

  typeChart = echarts.init(typeRef.value)
  typeChart.setOption({
    tooltip: { trigger: 'item', formatter: '{b}: {c} 条 ({d}%)' },
    legend: { bottom: 0, icon: 'circle', itemWidth: 8, itemHeight: 8 },
    color: ['#f56c6c', '#67c23a'],
    series: [
      {
        type: 'pie',
        radius: '62%',
        center: ['50%', '44%'],
        itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
        label: { formatter: '{b}\n{d}%' },
        data: typeDistribution.map((d) => ({ name: d.name, value: d.value })),
      },
    ],
  })
}

function onResize() {
  pieChart?.resize()
  typeChart?.resize()
}

onMounted(async () => {
  loading.value = true
  try {
    stats.value = await getDashboard()
    await nextTick()
    renderCharts()
    window.addEventListener('resize', onResize)
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', onResize)
  pieChart?.dispose()
  typeChart?.dispose()
})
</script>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-card {
  border-radius: var(--radius);
}

.stat-label {
  font-size: 13px;
  color: var(--text-sub);
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.1;
}

.unit {
  font-size: 13px;
  font-weight: 400;
  color: var(--text-sub);
  margin-left: 2px;
}

.stat-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.chart-card {
  border-radius: var(--radius);
}

.card-title {
  font-weight: 600;
}

.chart {
  height: 300px;
}

.rate-card {
  border-radius: var(--radius);
}

.rate-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 24px;
}

.rate-block {
  text-align: center;
}

.rate-label {
  font-size: 13px;
  color: var(--text-sub);
  margin-bottom: 10px;
}

.big-number {
  font-size: 32px;
  font-weight: 700;
  color: var(--brand);
}

.rate-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
}

.divider {
  height: 90px;
}
</style>
