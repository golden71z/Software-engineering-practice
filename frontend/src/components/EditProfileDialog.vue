<template>
  <el-dialog v-model="visible" title="修改个人信息" width="min(460px, 92vw)"
    :close-on-click-modal="false" :close-on-press-escape="!saving" :show-close="!saving"
    @open="fillForm" @closed="formRef?.clearValidate()">
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
      <el-form-item label="用户名">
        <el-input :model-value="user.profile?.username" disabled />
      </el-form-item>
      <el-form-item label="姓名" prop="real_name">
        <el-input v-model="form.real_name" maxlength="32" :disabled="saving" placeholder="请输入姓名（选填）" />
      </el-form-item>
      <el-form-item label="邮箱" prop="email">
        <el-input v-model="form.email" maxlength="128" :disabled="saving" placeholder="请输入邮箱" />
      </el-form-item>
      <el-form-item label="手机号" prop="phone">
        <el-input v-model="form.phone" maxlength="11" show-word-limit inputmode="numeric" :disabled="saving" placeholder="请输入 11 位手机号（选填）" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { updateMe } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const visible = defineModel({ type: Boolean, default: false })
const user = useUserStore()
const formRef = ref()
const saving = ref(false)
const form = reactive({ real_name: '', email: '', phone: '' })
const rules = {
  real_name: [{ max: 32, message: '姓名最多 32 个字', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
    { max: 128, message: '邮箱最多 128 位', trigger: 'blur' },
  ],
  phone: [{ pattern: /^1[3-9][0-9]{9}$/, message: '请输入有效的 11 位手机号', trigger: 'blur' }],
}

function fillForm() {
  form.real_name = user.profile?.real_name || ''
  form.email = user.profile?.email || ''
  form.phone = user.profile?.phone || ''
}

async function submit() {
  if (saving.value) return
  for (const key of Object.keys(form)) form[key] = form[key].trim()
  saving.value = true
  try {
    const valid = await formRef.value.validate().catch(() => false)
    if (!valid) {
      ElMessage.warning('请检查标红的输入项')
      return
    }
    const profile = await updateMe({
      email: form.email, real_name: form.real_name || null, phone: form.phone || null,
    })
    user.setProfile(profile)
    visible.value = false
    ElMessage.success('个人信息修改成功')
  } catch {
    /* 拦截器已提示，保留表单以便修改 */
  } finally {
    saving.value = false
  }
}
</script>
