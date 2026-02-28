import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user')) || null,
    token: localStorage.getItem('token') || null,
    tokenExpiry: localStorage.getItem('tokenExpiry') || null
  }),
  
  getters: {
    isAuthenticated: (state) => {
      // 检查token是否存在且未过期
      if (!state.token || !state.tokenExpiry) {
        return false
      }
      const now = new Date().getTime()
      const expiry = new Date(state.tokenExpiry).getTime()
      return now < expiry
    },
    isAdmin: (state) => state.user && state.user.is_admin
  },
  
  actions: {
    setUser(user) {
      this.user = user
      // 同时存储到localStorage
      localStorage.setItem('user', JSON.stringify(user))
    },
    
    setToken(token, expiresIn = 3600000*7*24) { // 默认1小时过期
      this.token = token
      const expiry = new Date()
      expiry.setTime(expiry.getTime() + expiresIn)
      this.tokenExpiry = expiry.toISOString()
      
      localStorage.setItem('token', token)
      localStorage.setItem('tokenExpiry', this.tokenExpiry)
    },
    
    logout() {
      this.user = null
      this.token = null
      this.tokenExpiry = null
      localStorage.removeItem('user')
      localStorage.removeItem('token')
      localStorage.removeItem('tokenExpiry')
    },
    
    // 检查token是否过期
    isTokenExpired() {
      if (!this.tokenExpiry) {
        return true
      }
      const now = new Date().getTime()
      const expiry = new Date(this.tokenExpiry).getTime()
      return now >= expiry
    }
  }
})