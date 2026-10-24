<template>
  <div>
    <!-- 首屏搜索 -->
    <section class="hero">
      <div class="hero-inner">
        <h1>丢了东西？捡到东西？</h1>
        <p>在校园里，让每一件失物都能找到主人</p>
        <div class="search-box">
          <el-input
            v-model="keyword"
            size="large"
            placeholder="试试搜索：校园卡、耳机、钥匙…"
            clearable
            @keyup.enter="goSearch"
          >
            <template #append>
              <el-button :icon="Search" @click="goSearch">搜索</el-button>
            </template>
          </el-input>
        </div>
        <div class="quick">
          <el-button size="large" type="danger" plain @click="goType('lost')">
            <el-icon><Warning /></el-icon> 我丢了东西
          </el-button>
          <el-button size="large" type="success" plain @click="goType('found')">
            <el-icon><CircleCheck /></el-icon> 我捡到东西
          </el-button>
        </div>
      </div>
    </section>

    <div class="page-container">
      <!-- 公告 -->
      <el-alert v-if="notices.length" type="info" show-icon :closable="false" class="notice">
        <template #default>
          <div class="notice-title">{{ notices[0].title }}</div>
          <div class="notice-content">{{ notices[0].content }}</div>
        </template>
      </el-alert>

      <!-- 最新发布 -->
      <div class="list-head">
        <h2 class="section-title">最新发布</h2>
        <el-button text type="primary" @click="router.push('/items')">
          查看全部 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <div v-loading="loading" class="grid">
        <ItemCard v-for="item in latest" :key="item.id" :item="item" />
      </div>

      <el-empty v-if="!loading && !latest.length" description="还没有发布任何信息" />

      <!-- 分栏入口 -->
      <div class="entries">
        <el-card shadow="never" class="entry" @click="goType('lost')">
          <div class="entry-icon lost"><el-icon :size="24"><Warning /></el-icon></div>
          <div>
            <div class="entry-title">失物信息</div>
            <div class="text-sub">同学们丢失的物品都在这里</div>
          </div>
        </el-card>
        <el-card shadow="never" class="entry" @click="goType('found')">
          <div class="entry-icon found"><el-icon :size="24"><CircleCheck /></el-icon></div>
          <div>
            <div class="entry-title">招领信息</div>
            <div class="text-sub">看看有没有你丢的东西</div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, CircleCheck, Search, Warning } from '@element-plus/icons-vue'
import ItemCard from '@/components/ItemCard.vue'
import { listItems } from '@/api/item'
import { listNotices } from '@/api/notice'

const router = useRouter()
const keyword = ref('')
const latest = ref([])
const notices = ref([])
const loading = ref(false)

function goSearch() {
  router.push({ path: '/items', query: keyword.value ? { keyword: keyword.value } : {} })
}

function goType(type) {
  router.push({ path: '/items', query: { type } })
}

onMounted(async () => {
  loading.value = true
  try {
    const [page, noticeList] = await Promise.all([
      listItems({ page: 1, size: 8 }),
      listNotices(3),
    ])
    latest.value = page.items || []
    notices.value = noticeList || []
  } catch {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 55%, #0ea5e9 100%);
  color: #fff;
  padding: 56px 20px 48px;
}

.hero-inner {
  max-width: 720px;
  margin: 0 auto;
  text-align: center;
}

.hero h1 {
  margin: 0 0 10px;
  font-size: 30px;
  letter-spacing: 1px;
}

.hero p {
  margin: 0 0 26px;
  opacity: 0.85;
  font-size: 14px;
}

.search-box {
  max-width: 520px;
  margin: 0 auto 18px;
}

.quick {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.notice {
  margin-bottom: 24px;
  border-radius: var(--radius);
}

.notice-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.notice-content {
  font-size: 13px;
  color: #4b5563;
  line-height: 1.6;
  white-space: pre-wrap;
}

.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
  min-height: 120px;
}

.entries {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 32px;
}

.entry {
  cursor: pointer;
  border-radius: var(--radius);
}

.entry :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 14px;
}

.entry-icon {
  width: 46px;
  height: 46px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.entry-icon.lost {
  background: #fef2f2;
  color: #dc2626;
}

.entry-icon.found {
  background: #ecfdf5;
  color: #059669;
}

.entry-title {
  font-weight: 600;
  margin-bottom: 2px;
}
</style>
