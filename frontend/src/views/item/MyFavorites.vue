<template>
  <div class="page-container" v-loading="loading">
    <div class="heading"><div><h1>我的收藏</h1><p>收藏的失物招领信息都在这里</p></div></div>
    <el-empty v-if="!loading && !items.length" description="还没有收藏物品" />
    <div v-else class="grid">
      <div v-for="item in items" :key="item.id" class="favorite">
        <ItemCard :item="item" />
        <el-button class="remove" type="danger" plain size="small" @click="unfavorite(item)">取消收藏</el-button>
      </div>
    </div>
    <div v-if="total > size" class="pagination"><el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next" @current-change="load" /></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import ItemCard from '@/components/ItemCard.vue'
import { listFavorites, removeFavorite } from '@/api/item'

const items = ref([]), loading = ref(false), page = ref(1), size = 12, total = ref(0)
async function load() {
  loading.value = true
  try { const data = await listFavorites({ page: page.value, size }); items.value = data.items; total.value = data.total }
  finally { loading.value = false }
}
async function unfavorite(item) {
  try { await removeFavorite(item.id); ElMessage.success('已取消收藏'); await load() } catch { /* 已提示 */ }
}
onMounted(load)
</script>

<style scoped>
.heading { margin-bottom: 22px; }
h1 { margin: 0 0 6px; font-size: 24px; }
p { margin: 0; color: var(--text-sub); }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.favorite { position: relative; padding-bottom: 38px; }
.remove { position: absolute; right: 0; bottom: 0; }
.pagination { display: flex; justify-content: center; margin-top: 28px; }
@media (max-width: 800px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
</style>
