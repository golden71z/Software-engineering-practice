<template>
  <div class="page-container" v-loading="loading">
    <div class="heading"><div><h1>疑似是我的</h1><p>先保存疑似相关的信息，核对后再提交认领</p></div></div>
    <el-empty v-if="!loading && !items.length" description="暂无待核实信息，可以在物品详情中标记“疑似是我的”" />
    <div v-else class="grid">
      <div v-for="item in items" :key="item.id" class="favorite">
        <ItemCard :item="item" />
        <div class="item-actions">
          <el-button type="primary" size="small" @click="goClaim(item)">去认领</el-button>
          <el-button type="danger" plain size="small" @click="unfavorite(item)">移出待核实</el-button>
        </div>
      </div>
    </div>
    <div v-if="total > size" class="pagination"><el-pagination v-model:current-page="page" :page-size="size" :total="total" layout="prev, pager, next" @current-change="load" /></div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ItemCard from '@/components/ItemCard.vue'
import { listFavorites, removeFavorite } from '@/api/item'

const items = ref([]), loading = ref(false), page = ref(1), size = 12, total = ref(0)
const router = useRouter()
async function load() {
  loading.value = true
  try { const data = await listFavorites({ page: page.value, size }); items.value = data.items; total.value = data.total }
  finally { loading.value = false }
}
async function unfavorite(item) {
  try { await removeFavorite(item.id); ElMessage.success('已移出待核实列表'); await load() } catch { /* 已提示 */ }
}
function goClaim(item) { router.push(`/items/${item.id}`) }
onMounted(load)
</script>

<style scoped>
.heading { margin-bottom: 22px; }
h1 { margin: 0 0 6px; font-size: 24px; }
p { margin: 0; color: var(--text-sub); }
.grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
.favorite { position: relative; padding-bottom: 38px; }
.item-actions { position: absolute; right: 0; bottom: 0; display: flex; gap: 8px; }
.pagination { display: flex; justify-content: center; margin-top: 28px; }
@media (max-width: 800px) { .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
@media (max-width: 520px) { .grid { grid-template-columns: 1fr; } }
</style>
