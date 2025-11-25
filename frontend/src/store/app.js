import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    activeApp: null,
    apps: []
  }),

  actions: {
    setActiveApp(app) {
      this.activeApp = app
    },

    setApps(apps) {
      this.apps = apps
    },

    addApp(app) {
      this.apps.push(app)
    },

    updateApp(app) {
      const index = this.apps.findIndex(a => a.id === app.id)
      if (index !== -1) {
        this.apps[index] = app
      }
    },

    removeApp(appId) {
      this.apps = this.apps.filter(a => a.id !== appId)
      if (this.activeApp?.id === appId) {
        this.activeApp = null
      }
    }
  }
})

