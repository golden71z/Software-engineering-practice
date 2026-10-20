<template>
  <div class="page-container">
    <el-page-header :content="isEdit ? '编辑信息' : '发布信息'" class="back" @back="router.back()" />

    <el-card shadow="never" class="form-card" v-loading="loading">
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="92px"
        label-position="right"
      >
        <el-form-item label="信息类型" prop="type">
          <el-radio-group v-model="form.type">
            <el-radio-button value="lost">我丢了东西（失物）</el-radio-button>
            <el-radio-button value="found">我捡到东西（招领）</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="标题" prop="title">
          <el-input
            v-model="form.title"
            maxlength="100"
            show-word-limit
            placeholder="一句话说清楚，例如：丢失一张校园一卡通"
          />
        </el-form-item>

        <el-form-item label="物品分类" prop="category_id">
          <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 240px">
            <el-option v-for="c in categories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>

        <el-form-item :label="form.type === 'lost' ? '丢失时间' : '拾获时间'" prop="event_time">
          <el-date-picker
            v-model="form.event_time"
            type="datetime"
            placeholder="选择时间"
            value-format="YYYY-MM-DDTHH:mm:ss"
            style="width: 240px"
          />
        </el-form-item>

        <el-form-item label="地点" prop="location">
          <el-input v-model="form.location" maxlength="100" placeholder="例如：第二食堂二楼" />
        </el-form-item>

        <el-form-item label="详细描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="5"
            maxlength="2000"
            show-word-limit
            placeholder="描述物品特征（颜色、品牌、内含物等），细节越具体越容易核对"
          />
        </el-form-item>

        <el-form-item label="联系方式">
          <el-input
            v-model="form.contact"
            maxlength="64"
            placeholder="手机号或微信号（仅登录用户可见）"
            style="width: 320px"
          />
        </el-form-item>

        <el-form-item label="物品图片">
          <el-upload
            v-model:file-list="fileList"
            list-type="picture-card"
            :http-request="doUpload"
            :limit="4"
            accept="image/*"
            :on-remove="onRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="text-sub">最多 4 张，单张不超过 5MB</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="onSubmit">
            {{ isEdit ? '保存修改' : '立即发布' }}
          </el-button>
          <el-button @click="router.back()">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { createItem, getItem, updateItem } from '@/api/item'
import { listCategories } from '@/api/category'
import { uploadImage } from '@/api/upload'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const isEdit = computed(() => Boolean(route.query.id))
const formRef = ref()
const loading = ref(false)
const submitting = ref(false)
const categories = ref([])
const fileList = ref([])

const form = reactive({
  type: 'lost',
  title: '',
  category_id: null,
  event_time: '',
  location: '',
  description: '',
  contact: '',
  images: [],
})

const rules = {
  type: [{ required: true, message: '请选择信息类型', trigger: 'change' }],
  title: [
    { required: true, message: '请填写标题', trigger: 'blur' },
    { min: 2, max: 100, message: '长度为 2-100 字', trigger: 'blur' },
  ],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  event_time: [{ required: true, message: '请选择时间', trigger: 'change' }],
  location: [{ required: true, message: '请填写地点', trigger: 'blur' }],
  description: [
    { required: true, message: '请填写详细描述', trigger: 'blur' },
    { min: 5, message: '描述至少 5 个字', trigger: 'blur' },
  ],
}

/** 自定义上传：直接调后端接口，返回的相对路径存进 fileList */
async function doUpload(options) {
  try {
    const data = await uploadImage(options.file)
    options.onSuccess(data)
    fileList.value = fileList.value.map((f) =>
      f.uid === options.file.uid ? { ...f, url: data.url, response: data } : f
    )
  } catch (err) {
    options.onError(err)
  }
}

function onRemove() {
  // 只从本地列表移除，后端文件保留（课程作业不做垃圾回收）
}

function syncImages() {
  form.images = fileList.value
    .map((f) => f.response?.url || f.url)
    .filter((u) => typeof u === 'string' && u.startsWith('/static/'))
}

async function onSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  syncImages()
  submitting.value = true
  try {
    const payload = {
      type: form.type,
      title: form.title.trim(),
      description: form.description.trim(),
      category_id: form.category_id,
      event_time: form.event_time,
      location: form.location.trim(),
      contact: form.contact.trim() || null,
      images: form.images,
    }

    if (isEdit.value) {
      await updateItem(route.query.id, payload)
      ElMessage.success('修改成功')
      router.push(`/items/${route.query.id}`)
    } else {
      const created = await createItem(payload)
      ElMessage.success('发布成功')
      router.push(`/items/${created.id}`)
    }
  } catch {
    // 拦截器已提示
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    categories.value = await listCategories()

    if (isEdit.value) {
      const detail = await getItem(route.query.id)
      if (detail.publisher_id !== user.profile?.id) {
        ElMessage.error('只能编辑自己发布的信息')
        router.replace('/')
        return
      }
      Object.assign(form, {
        type: detail.type,
        title: detail.title,
        category_id: detail.category_id,
        event_time: detail.event_time,
        location: detail.location,
        description: detail.description,
        contact: detail.contact || '',
        images: detail.images || [],
      })
      fileList.value = (detail.images || []).map((url, idx) => ({
        name: `图片${idx + 1}`,
        url,
      }))
    } else {
      form.contact = user.profile?.phone || ''
    }
  } catch {
    /* 已提示 */
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.back {
  margin-bottom: 16px;
}

.form-card {
  border-radius: var(--radius);
  max-width: 780px;
}
</style>
