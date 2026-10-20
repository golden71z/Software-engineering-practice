<template>
  <el-card shadow="hover" class="item-card" :body-style="{ padding: '0' }" @click="goDetail">
    <div class="cover">
      <img v-if="item.images && item.images.length" :src="item.images[0]" alt="物品图片" />
      <div v-else class="cover-placeholder">
        <el-icon :size="34"><Picture /></el-icon>
      </div>
      <el-tag class="type-tag" :type="typeTagType(item.type)" effect="dark" size="small">
        {{ TYPE_TEXT[item.type] }}
      </el-tag>
    </div>

    <div class="body">
      <div class="title" :title="item.title">{{ item.title }}</div>
      <div class="desc">{{ item.description }}</div>

      <div class="meta">
        <span><el-icon><Location /></el-icon>{{ item.location }}</span>
        <span><el-icon><Clock /></el-icon>{{ formatDate(item.event_time) }}</span>
      </div>

      <div class="footer">
        <el-tag size="small" type="info" effect="plain">{{ item.category_name }}</el-tag>
        <el-tag v-if="item.status !== 'published'" size="small" :type="itemStatusType(item.status)">
          {{ ITEM_STATUS_TEXT[item.status] }}
        </el-tag>
        <span class="time">{{ fromNow(item.created_at) }}</span>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { Clock, Location, Picture } from '@element-plus/icons-vue'
import {
  ITEM_STATUS_TEXT,
  TYPE_TEXT,
  formatDate,
  fromNow,
  itemStatusType,
  typeTagType,
} from '@/utils/format'

const props = defineProps({
  item: { type: Object, required: true },
})

const router = useRouter()

function goDetail() {
  router.push(`/items/${props.item.id}`)
}
</script>

<style scoped>
.item-card {
  cursor: pointer;
  border-radius: var(--radius);
  overflow: hidden;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.item-card:hover {
  transform: translateY(-2px);
}

.cover {
  position: relative;
  height: 150px;
  background: #f3f4f6;
  overflow: hidden;
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cbd5e1;
  background: linear-gradient(135deg, #f8fafc, #eef2f7);
}

.type-tag {
  position: absolute;
  top: 10px;
  left: 10px;
}

.body {
  padding: 14px 16px 16px;
}

.title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.desc {
  font-size: 13px;
  color: var(--text-sub);
  line-height: 1.55;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 10px;
}

.meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.footer {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}
</style>
