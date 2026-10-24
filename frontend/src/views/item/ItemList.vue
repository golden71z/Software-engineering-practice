<template>
  <div class="page-container">
    <div class="filter-bar">
      <el-radio-group v-model="query.type" @change="reload">
        <el-radio-button :value="''">全部</el-radio-button>
        <el-radio-button value="lost">失物</el-radio-button>
        <el-radio-button value="found">招领</el-radio-button>
      </el-radio-group>

      <el-select
        v-model="query.category_id"
        placeholder="全部分类"
        clearable
        style="width: 150px"
        @change="reload"
      >
        <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>

      <el-input
        v-model="query.keyword"
        placeholder="搜索标题、描述或地点"
        clearable
        style="width: 260px"
        :prefix-icon="Search"
        @keyup.enter="reload"
        @clear="reload"
      />

      <el-button type="primary" @click="reload">搜索</el-button>

      <div class="spacer" />

      <el-button :icon="Plus" @click="goPublish">发布信息</el-button>
    </div>

    <div v-loading="loading" class="grid">
      <ItemCard v-for="item in list" :key="item.id" :item="item" />
    </div>

    <el-empty v-if="!loading && !list.length" description="没有找到符合条件的信息" />

    <div v-if="total > 0" class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[12, 24, 48]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="reload"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import ItemCard from '@/components/ItemCard.vue'
import { listItems } from '@/api/item'
import { listCategories } from '@/api/category'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const loading = ref(false)
const list = ref([])
const total = ref(0)
const categories = ref([])

const query = reactive({
  type: typeof route.query.type === 'string' ? route.query.type : '',
  category_id: null,
  keyword: typeof route.query.keyword === 'string' ? route.query.keyword : '',
  page: 1,
  size: 12,
})

async function load() {
  loading.value = true
  try {
    const data = await listItems({
      type: query.type || undefined,
      category_id: query.category_id || undefined,
      keyword: query.keyword || undefined,
      page: query.page,
      size: query.size,
    })
    list.value = data.items || []
    total.value = data.total || 0
  } catch {
    // 拦截器已提示
  } finally {
    loading.value = false
  }
}

function reload() {
  query.page = 1
  load()
}

function goPublish() {
  if (!user.isLogin) {
    ElMessageBox.confirm('发布信息需要先登录，是否前往登录？', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() => router.push({ path: '/login', query: { redirect: '/publish' } }))
      .catch(() => {})
    return
  }
  router.push('/publish')
}

onMounted(async () => {
  load()
  try {
    categories.value = await listCategories()
  } catch {
    categories.value = []
  }
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  padding: 14px 16px;
  border-radius: var(--radius);
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.spacer {
  flex: 1;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 16px;
  min-height: 160px;
}

.pager {
  display: flex;
  justify-content: center;
  margin-top: 26px;
}
</style>
