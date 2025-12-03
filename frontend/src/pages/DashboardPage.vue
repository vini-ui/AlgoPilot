<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-6">Dashboard</h1>
      
      <!-- Active App Header -->
      <div v-if="activeApp" class="card mb-6">
        <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <h2 class="text-2xl font-display font-semibold text-gray-900 dark:text-white">
                {{ activeApp.name }}
              </h2>
              <span
                :class="[
                  'px-3 py-1 text-xs font-medium rounded-full',
                  activeApp.status === 'active'
                    ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-dark-700 dark:text-gray-300'
                ]"
              >
                {{ activeApp.status }}
              </span>
              <span
                v-if="activeApp.is_default"
                class="px-3 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
              >
                Default
              </span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Account ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ activeApp.account_id }}</p>
                </div>
              </div>
              
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
                </svg>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Base URL</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white break-all">{{ activeApp.base_url }}</p>
                </div>
              </div>
              
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Created</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatDate(activeApp.created_at) }}</p>
                </div>
              </div>
              
              <div class="flex items-start gap-2">
                <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
                <div>
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">App ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">#{{ activeApp.id }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="flex gap-2 md:flex-col">
            <button
              @click="$router.push('/apps')"
              class="btn-secondary text-sm whitespace-nowrap"
            >
              <svg class="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              Switch App
            </button>
          </div>
        </div>
      </div>
      
      <!-- No Active App Message -->
      <div v-else class="card mb-6">
        <div class="text-center py-8">
          <svg class="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
          </svg>
          <p class="text-gray-600 dark:text-gray-400 mb-4 text-lg font-medium">No active app selected</p>
          <button
            @click="$router.push('/apps')"
            class="btn-primary"
          >
            <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Select an App
          </button>
        </div>
      </div>
      
      <div class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <p class="text-gray-500 dark:text-gray-400 text-lg">Dashboard content coming soon...</p>
        <p class="text-gray-400 dark:text-gray-500 mt-2">This will show overall app statistics, active strategies, and recent activity.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAppStore } from '../store/app'
import apiClient from '../api/client'

export default {
  name: 'DashboardPage',
  setup() {
    const appStore = useAppStore()
    
    const activeApp = computed(() => appStore.activeApp)
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        })
      } catch (e) {
        return dateString
      }
    }

    const loadApps = async () => {
      try {
        const response = await apiClient.get('/apps')
        appStore.setApps(response.data)
        
        // If we have an active app from localStorage, try to find and update it
        if (appStore.activeApp) {
          const updatedApp = response.data.find(app => app.id === appStore.activeApp.id)
          if (updatedApp) {
            // Merge persisted app data with fresh data from server
            appStore.setActiveApp({
              ...updatedApp,
              // Preserve status if it was active, otherwise use server status
              status: appStore.activeApp.status === 'active' ? 'active' : updatedApp.status
            })
          }
        }
      } catch (error) {
        console.error('Failed to load apps:', error)
      }
    }
    
    onMounted(() => {
      // Load apps on mount to ensure we have fresh data
      loadApps()
    })
    
    return {
      activeApp,
      formatDate
    }
  }
}
</script>

