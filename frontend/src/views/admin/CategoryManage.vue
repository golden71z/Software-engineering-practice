<template>
  <el-card shadow="never" class="card">
    <div class="toolbar">
      <el-button type="primary" :icon="Plus" @click="openCreate">新增分类</el-button>
      <el-checkbox v-model="includeInactive" @change="load">显示已停用的分类</el-checkbox>
      <span class="text-sub">被信息引用过的分类不能删除，只能停用</span>
    </div>

    <el-table :data="list" v-loading="loading" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="分类名称" min-width="180" />
      <el-table-column prop="sort_order" label="排序值" width="100" />
      <el-table-column label="状态" width="110">
        <template #default="{ row }">
          <el-tag size="small" :type="row.is_active === 1 ? 'success' : 'info'">
            {{ row.is_active === 1 ? '启用' : '已停用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button
            link
            :type="row.is_active === 1 ? 'warning' : 'success'"
            @click="toggleActive(row)"
          >
            {{ row.is_active === 1 ? '停用' : '启用' }}
          </el-button>
          <el-button link type="danger" @click="onDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="editing ? '编辑分类' : '新增分类'" width="420px">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="form.name" maxlength="32" placeholder="例如：证件卡片" />
        </el-form-item>
        <el-form-item label="排序值">
          <el-input-number v-model="form.sort_order" :min="0" :max="999" />
          <span class="text-sub ml">越小越靠前</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="onSave">保存</el-button>
      </template>
    </el-dialog>
  </el-card>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  createCategory,
  listCategories,
  removeCategory,
  updateCategory,
} from '@/api/category'

const list = ref([])
const loading = ref(false)
const saving = ref(false)
const includeInactive = ref(true)
const dialogVisible = ref(false)
const editing = ref(null)
const formRef = ref()

const form = reactive({ name: '', sort_order: 0 })
const rules = { name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }] }

async function load() {
  loading.value = true
  try {
    list.value = await listCategories(!includeInactive.value)
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.name = ''
  form.sort_order = 0
  dialogVisible.value = true
}

function openEdit(row) {
  editing.value = row
  form.name = row.name
  form.sort_order = row.sort_order
  dialogVisible.value = true
}

async function onSave() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editing.value) {
      await updateCategory(editing.value.id, { ...form })
      ElMessage.success('修改成功')
    } else {
      await createCategory({ ...form })
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    load()
  } catch {
    /* 已提示 */
  } finally {
    saving.value = false
  }
}

async function toggleActive(row) {
  try {
    await updateCategory(row.id, { is_active: row.is_active === 1 ? 0 : 1 })
    ElMessage.success('已更新状态')
    load()
  } catch {
    /* 已提示 */
  }
}

async function onDelete(row) {
  const confirmed = await ElMessageBox.confirm(
    `确认删除分类「${row.name}」？如果已有信息使用该分类，删除会被拒绝。`,
    '删除分类',
    { type: 'warning' }
  ).catch(() => false)
  if (!confirmed) return

  try {
    await removeCategory(row.id)
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

.ml {
  margin-left: 10px;
}
</style>
