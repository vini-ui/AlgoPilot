import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    isAuthenticated: false,
    sessionToken: null,
    user: null
  }),

  actions: {
    login(token, user) {
      this.isAuthenticated = true
      this.sessionToken = token
      this.user = user
    },

    logout() {
      this.isAuthenticated = false
      this.sessionToken = null
      this.user = null
    }
  }
})

