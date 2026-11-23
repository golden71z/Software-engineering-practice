<template>
  <el-dialog
    v-model="visible"
    title="修改密码"
    width="min(460px, 92vw)"
    :close-on-click-modal="false"
    :close-on-press-escape="!saving"
    :show-close="!saving"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
      <el-form-item label="当前密码" prop="current_password">
        <el-input v-model="form.current_password" type="password" show-password autocomplete="current-password" maxlength="64" :disabled="saving" placeholder="请输入当前密码" />
      </el-form-item>
      <el-form-item label="新密码" prop="new_password">
        <el-input v-model="form.new_password" type="password" show-password autocomplete="new-password" maxlength="64" :disabled="saving" placeholder="请输入 6–64 位新密码" />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirm">
        <el-input v-model="form.confirm" type="password" show-password autocomplete="new-password" maxlength="64" :disabled="saving" placeholder="请再次输入新密码" @keyup.enter="submit" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button :disabled="saving" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="submit">确认修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'
import { useUserStore } from '@/stores/user'

const visible = defineModel({ type: Boolean, default: false })
const router = useRouter()
const user = useUserStore()
const formRef = ref()
const saving = ref(false)
const form = reactive({ current_password: '', new_password: '', confirm: '' })
const rules = {
  current_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 64, message: '新密码长度为 6–64 位', trigger: 'blur' },
    { validator: (_rule, value, callback) => {
      if (value === form.current_password) callback(new Error('新密码不能与当前密码相同'))
      else if (new TextEncoder().encode(value).length > 72) callback(new Error('新密码 UTF-8 长度不能超过 72 字节'))
      else callback()
    }, trigger: 'blur' },
  ],
  confirm: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: (_rule, value, callback) => {
      if (value !== form.new_password) callback(new Error('两次输入的新密码不一致'))
      else callback()
    }, trigger: 'blur' },
  ],
}

function resetForm() {
  form.current_password = ''
  form.new_password = ''
  form.confirm = ''
  formRef.value?.clearValidate()
}

async function submit() {
  if (saving.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) {
    ElMessage.warning('请检查标红的输入项')
    return
  }
  saving.value = true
  try {
    await changePassword({ current_password: form.current_password, new_password: form.new_password })
    visible.value = false
    resetForm()
    user.logout()
    ElMessage.success('密码修改成功，请使用新密码重新登录')
    router.replace('/login')
  } catch {
    /* 拦截器已提示，保留表单以便修改 */
  } finally {
    saving.value = false
  }
}
</script>
