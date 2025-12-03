import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => {
    // Try to load activeApp from localStorage on initialization
    let initialActiveApp = null
    try {
      const stored = localStorage.getItem('activeApp')
      if (stored) {
        initialActiveApp = JSON.parse(stored)
      }
    } catch (e) {
      console.error('Error reading activeApp from localStorage:', e)
    }

    // Try to load session from localStorage on initialization
    let initialSession = null
    try {
      const stored = localStorage.getItem('smartapiSession')
      if (stored) {
        initialSession = JSON.parse(stored)
      }
    } catch (e) {
      console.error('Error reading session from localStorage:', e)
    }

    return {
      activeApp: initialActiveApp,
      apps: [],
      session: initialSession
    }
  },

  actions: {
    setActiveApp(app) {
      this.activeApp = app
      // Persist to localStorage
      try {
        if (app) {
          localStorage.setItem('activeApp', JSON.stringify(app))
        } else {
          localStorage.removeItem('activeApp')
        }
      } catch (e) {
        console.error('Error storing activeApp to localStorage:', e)
      }
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
        this.setActiveApp(null) // Use setActiveApp to also clear localStorage
      }
    },

    setSession(sessionData) {
      this.session = sessionData
      // Also store in localStorage for persistence
      try {
        localStorage.setItem('smartapiSession', JSON.stringify(sessionData))
      } catch (e) {
        console.error('Error storing session to localStorage:', e)
      }
    },

    getSession() {
      if (this.session) {
        return this.session
      }
      // Try to load from localStorage
      try {
        const stored = localStorage.getItem('smartapiSession')
        if (stored) {
          this.session = JSON.parse(stored)
          return this.session
        }
      } catch (e) {
        console.error('Error reading session from localStorage:', e)
      }
      return null
    },

    clearSession() {
      this.session = null
      try {
        localStorage.removeItem('smartapiSession')
      } catch (e) {
        console.error('Error removing session from localStorage:', e)
      }
    },

    // Initialize store - load persisted data
    initialize() {
      // Active app is already loaded in state initialization
      // Session is already loaded in state initialization
      // This method can be used for any additional initialization
    }
  }
})

