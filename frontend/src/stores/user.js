import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { getMe, login as loginApi } from '@/api/auth'

const TOKEN_KEY = 'lf_token'
const PROFILE_KEY = 'lf_profile'

/**
 * 登录态 Store。
 *
 * token 存在 localStorage：刷新页面不掉线，代价是 XSS 可以偷走。
 * 生产环境应改用 HttpOnly Cookie + CSRF Token —— 这点要写进设计文档的权衡分析里。
 */
export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const profile = ref(safeParse(localStorage.getItem(PROFILE_KEY)))

  const isLogin = computed(() => Boolean(token.value))
  const isAdmin = computed(() => profile.value?.role === 'admin')
  const displayName = computed(() => profile.value?.real_name || profile.value?.username || '游客')

  function setToken(value) {
    token.value = value || ''
    if (value) localStorage.setItem(TOKEN_KEY, value)
    else localStorage.removeItem(TOKEN_KEY)
  }

  function setProfile(value) {
    profile.value = value || null
    if (value) localStorage.setItem(PROFILE_KEY, JSON.stringify(value))
    else localStorage.removeItem(PROFILE_KEY)
  }

  function clear() {
    setToken('')
    setProfile(null)
  }

  async function login(payload) {
    const data = await loginApi(payload)
    setToken(data.access_token)
    await fetchProfile()
  }

  async function fetchProfile() {
    const me = await getMe()
    setProfile(me)
    return me
  }

  function logout() {
    clear()
  }

  return {
    token,
    profile,
    isLogin,
    isAdmin,
    displayName,
    login,
    logout,
    clear,
    fetchProfile,
    setToken,
    setProfile,
  }
})

function safeParse(raw) {
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}
