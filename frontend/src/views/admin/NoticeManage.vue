<template>
  <el-card shadow="never" class="card">
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="openCreate">发布公告</el-button>
      <span class="text-sub">公告会显示在首页顶部，建议控制在一屏内</span>
    </div>

    <div v-for="n in list" :key="n.id" class="notice-item">
      <div class="notice-head">
        <div class="title">
          <el-tag v-if="n.is_top === 1" size="small" type="danger" effect="plain">置顶</el-tag>
          <span>{{ n.title }}</span>
        </div>
        <div class="ops">
          <span class="text-sub">{{ formatTime(n.created_at) }}</span>
          <el-button link type="danger" @click="onDelete(n)">删除</el-button>
        </div>
      </div>
      <p class="content">{{ n.content }}</p>
    </div>

    <el-empty v-if="!loading && !list.length" description="还没有发布公告" />

    <el-dialog v-model="dialogVisible" title="发布公告" width="560px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="70px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" maxlength="100" show-word-limit />
        </el-form-item>
        <el-form-item label="正文" prop="content">
          <el-input
            v-model="form.content"
            type="textarea"
            :rows="5"
            maxlength="2000"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_top" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">发布</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createNotice, listNotices, removeNotice } from '@/api/notice'
import { formatTime } from '@/utils/format'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const formRef = ref()

const form = reactive({ title: '', content: '', is_top: 0 })

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  content: [{ required: true, message: '请输入正文', trigger: 'blur' }],
}

async function load() {
  loading.value = true
  try {
    list.value = (await listNotices()) || []
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

function openCreate() {
  form.title = ''
  form.content = ''
  form.is_top = 0
  dialogVisible.value = true
}

async function onSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await createNotice({ ...form })
    ElMessage.success('已发布')
    dialogVisible.value = false
    load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

async function onDelete(row) {
  const confirmed = await ElMessageBox.confirm(`确认删除公告「${row.title}」？`, '提示', {
    type: 'warning',
  }).catch(() => false)
  if (!confirmed) return

  try {
    await removeNotice(row.id)
    ElMessage.success('已删除')
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

.toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.notice-item {
  padding: 16px 4px;
  border-bottom: 1px solid #f1f5f9;
}

.notice-item:last-of-type {
  border-bottom: none;
}

.notice-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.ops {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content {
  margin: 0;
  font-size: 13px;
  color: #4b5563;
  line-height: 1.7;
  white-space: pre-wrap;
}
</style>
