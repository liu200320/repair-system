import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as apiLogin } from '../api/auth'

const TOKEN_KEY = 'repair_token'
const USER_KEY  = 'repair_user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user  = ref(JSON.parse(localStorage.getItem(USER_KEY) || 'null'))

  const isLoggedIn = computed(() => !!token.value)
  const isAdmin    = computed(() => user.value?.role === 'admin')

  async function doLogin(username, password) {
    const res = await apiLogin({ username, password })
    token.value = res.access_token
    user.value  = res.user
    localStorage.setItem(TOKEN_KEY, res.access_token)
    localStorage.setItem(USER_KEY,  JSON.stringify(res.user))
  }

  function logout() {
    token.value = ''
    user.value  = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  return { token, user, isLoggedIn, isAdmin, doLogin, logout }
})
