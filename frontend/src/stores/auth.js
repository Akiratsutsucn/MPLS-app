import { defineStore } from 'pinia'
import { login as apiLogin, register as apiRegister, getMe } from '../api/auth.js'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('token') || null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
  },

  actions: {
    async login(data) {
      const res = await apiLogin(data)
      this.token = res.data.access_token
      localStorage.setItem('token', this.token)
      await this.fetchUser()
    },

    async register(data) {
      await apiRegister(data)
    },

    async fetchUser() {
      const res = await getMe()
      this.user = res.data
    },

    logout() {
      this.user = null
      this.token = null
      localStorage.removeItem('token')
    },
  },
})
