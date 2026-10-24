<template>
  <div class="page-container" v-loading="loading">
    <el-page-header content="信息详情" class="back" @back="router.back()" />

    <template v-if="item">
      <el-card shadow="never" class="detail-card">
        <div class="detail-grid">
          <!-- 图片区 -->
          <div class="gallery">
            <el-carousel v-if="item.images.length" height="340px" :autoplay="false">
              <el-carousel-item v-for="(img, idx) in item.images" :key="idx">
                <el-image :src="img" fit="contain" class="gallery-img" :preview-src-list="item.images" />
              </el-carousel-item>
            </el-carousel>
            <div v-else class="gallery-empty">
              <el-icon :size="46"><Picture /></el-icon>
              <span>发布者未上传图片</span>
            </div>
          </div>

          <!-- 信息区 -->
          <div class="info">
            <div class="tag-row">
              <el-tag :type="typeTagType(item.type)" effect="dark">
                {{ TYPE_TEXT[item.type] }}
              </el-tag>
              <el-tag :type="itemStatusType(item.status)" effect="plain">
                {{ ITEM_STATUS_TEXT[item.status] }}
              </el-tag>
              <el-tag type="info" effect="plain">{{ item.category_name }}</el-tag>
            </div>

            <h1>{{ item.title }}</h1>

            <div class="meta-list">
              <div class="meta-row">
                <span class="label">发生地点</span>
                <span>{{ item.location }}</span>
              </div>
              <div class="meta-row">
                <span class="label">{{ item.type === 'lost' ? '丢失时间' : '拾获时间' }}</span>
                <span>{{ formatTime(item.event_time) }}</span>
              </div>
              <div class="meta-row">
                <span class="label">发布时间</span>
                <span>{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="meta-row">
                <span class="label">发布者</span>
                <span>{{ item.publisher_name }}</span>
              </div>
              <div class="meta-row">
                <span class="label">联系方式</span>
                <span v-if="item.contact || item.publisher_phone">
                  {{ item.contact || item.publisher_phone }}
                </span>
                <span v-else class="text-sub">
                  {{ user.isLogin ? '发布者未留联系方式' : '登录后可见' }}
                </span>
              </div>
              <div class="meta-row">
                <span class="label">浏览次数</span>
                <span>{{ item.view_count }}</span>
              </div>
            </div>

            <el-divider content-position="left">详细描述</el-divider>
            <p class="description">{{ item.description }}</p>

            <!-- 操作区 -->
            <div class="actions">
              <template v-if="isOwner">
                <el-button :icon="Edit" @click="router.push(`/publish?id=${item.id}`)">
                  编辑
                </el-button>
                <el-button
                  v-if="item.status === 'published'"
                  type="success"
                  @click="onMarkReturned"
                >
                  标记已归还
                </el-button>
                <el-button v-if="item.status !== 'offline'" type="warning" plain @click="onOffline">
                  下架
                </el-button>
                <el-button v-else type="primary" plain @click="onRestore">重新上架</el-button>
              </template>

              <template v-else>
                <el-button
                  type="primary"
                  size="large"
                  :disabled="item.status !== 'published'"
                  @click="openClaim"
                >
                  我要认领
                </el-button>
                <span v-if="item.status !== 'published'" class="text-sub">
                  该信息当前不接受认领
                </span>
              </template>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 认领弹窗 -->
      <el-dialog v-model="claimVisible" title="提交认领申请" width="520px">
        <el-alert
          type="info"
          :closable="false"
          show-icon
          title="请尽量描述只有失主才知道的细节，便于发布者核对"
          class="claim-tip"
        />
        <el-form ref="claimFormRef" :model="claimForm" :rules="claimRules" label-position="top">
          <el-form-item label="认领说明" prop="proof">
            <el-input
              v-model="claimForm.proof"
              type="textarea"
              :rows="4"
              maxlength="500"
              show-word-limit
              placeholder="例如：卡套颜色、卡号后四位、物品内含物、特殊痕迹等"
            />
          </el-form-item>
          <el-form-item label="联系方式">
            <el-input v-model="claimForm.contact" placeholder="手机号或微信号，方便发布者联系你" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="claimVisible = false">取消</el-button>
          <el-button type="primary" :loading="claiming" @click="submitClaim">提交申请</el-button>
        </template>
      </el-dialog>
    </template>

    <el-empty v-else-if="!loading" description="信息不存在或已下架" />
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Edit, Picture } from '@element-plus/icons-vue'
import { getItem, markReturned, offlineItem, restoreItem } from '@/api/item'
import { applyClaim } from '@/api/claim'
import { useUserStore } from '@/stores/user'
import {
  ITEM_STATUS_TEXT,
  TYPE_TEXT,
  formatTime,
  itemStatusType,
  typeTagType,
} from '@/utils/format'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const loading = ref(false)
const item = ref(null)
const claimVisible = ref(false)
const claiming = ref(false)
const claimFormRef = ref()
const claimForm = reactive({ proof: '', contact: '' })

const claimRules = {
  proof: [
    { required: true, message: '请填写认领说明', trigger: 'blur' },
    { min: 5, message: '至少写 5 个字，太简短无法核对', trigger: 'blur' },
  ],
}

const isOwner = computed(
  () => user.isLogin && item.value && item.value.publisher_id === user.profile?.id
)

async function load() {
  loading.value = true
  try {
    item.value = await getItem(route.params.id)
  } catch {
    item.value = null
  } finally {
    loading.value = false
  }
}

function openClaim() {
  if (!user.isLogin) {
    ElMessageBox.confirm('认领需要先登录，是否前往登录？', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning',
    })
      .then(() =>
        router.push({ path: '/login', query: { redirect: route.fullPath } })
      )
      .catch(() => {})
    return
  }
  claimForm.proof = ''
  claimForm.contact = user.profile?.phone || ''
  claimVisible.value = true
}

async function submitClaim() {
  const valid = await claimFormRef.value.validate().catch(() => false)
  if (!valid) return

  claiming.value = true
  try {
    await applyClaim({
      item_id: item.value.id,
      proof: claimForm.proof,
      contact: claimForm.contact || null,
    })
    ElMessage.success('申请已提交，等待发布者处理')
    claimVisible.value = false
  } catch {
    // 拦截器已提示
  } finally {
    claiming.value = false
  }
}

async function onMarkReturned() {
  await ElMessageBox.confirm('确认这件物品已经归还？标记后不可再修改。', '提示', {
    type: 'warning',
  }).catch(() => Promise.reject(new Error('cancel')))
  try {
    item.value = await markReturned(item.value.id)
    ElMessage.success('已标记为归还')
  } catch {
    /* 已提示 */
  }
}

async function onOffline() {
  await ElMessageBox.confirm('下架后其他同学将看不到这条信息，确认下架？', '提示', {
    type: 'warning',
  }).catch(() => Promise.reject(new Error('cancel')))
  try {
    item.value = await offlineItem(item.value.id)
    ElMessage.success('已下架')
  } catch {
    /* 已提示 */
  }
}

async function onRestore() {
  try {
    item.value = await restoreItem(item.value.id)
    ElMessage.success('已重新上架')
  } catch {
    /* 已提示 */
  }
}

onMounted(load)
watch(() => route.params.id, load)
</script>

<style scoped>
.back {
  margin-bottom: 16px;
}

.detail-card {
  border-radius: var(--radius);
}

.detail-grid {
  display: grid;
  grid-template-columns: 380px 1fr;
  gap: 28px;
}

.gallery {
  background: #f8fafc;
  border-radius: var(--radius);
  overflow: hidden;
}

.gallery-img {
  width: 100%;
  height: 100%;
}

.gallery-empty {
  height: 340px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  color: #cbd5e1;
  font-size: 13px;
}

.tag-row {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

h1 {
  margin: 0 0 18px;
  font-size: 22px;
  line-height: 1.4;
}

.meta-list {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
  background: #f9fafb;
  padding: 14px 16px;
  border-radius: 8px;
}

.meta-row {
  display: flex;
  gap: 10px;
  font-size: 13px;
}

.meta-row .label {
  color: var(--text-sub);
  min-width: 62px;
}

.description {
  white-space: pre-wrap;
  line-height: 1.8;
  font-size: 14px;
  color: #374151;
  margin: 0;
}

.actions {
  margin-top: 26px;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.claim-tip {
  margin-bottom: 16px;
}

@media (max-width: 900px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .meta-list {
    grid-template-columns: 1fr;
  }
}
</style>
