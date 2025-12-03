<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-8">
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white">App Selector</h1>
        <button
          @click="showAddModal = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add New App
        </button>
      </div>

      <div v-if="loading" class="text-center py-16">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400 font-medium">Loading apps...</p>
      </div>

      <div v-else-if="apps.length === 0" class="text-center py-16">
        <svg class="mx-auto h-16 w-16 text-gray-400 dark:text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
        </svg>
        <p class="text-gray-600 dark:text-gray-400 mb-6 text-lg font-medium">No apps configured yet.</p>
        <button
          @click="showAddModal = true"
          class="btn-primary"
        >
          <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Add Your First App
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="app in apps"
          :key="app.id"
          class="card hover:shadow-xl transition-all duration-300"
        >
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-display font-semibold text-gray-900 dark:text-white">{{ app.name }}</h3>
            <span
              :class="[
                'px-3 py-1 text-xs font-medium rounded-full',
                app.status === 'active' 
                  ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200' 
                  : 'bg-gray-100 text-gray-800 dark:bg-dark-700 dark:text-gray-300'
              ]"
            >
              {{ app.status }}
            </span>
          </div>
          
          <p class="text-gray-600 dark:text-gray-400 mb-4">
            <span class="font-medium">Account:</span> {{ app.account_id }}
          </p>
          
          <div class="flex items-center mb-6">
            <input
              :id="`default-${app.id}`"
              type="checkbox"
              :checked="app.is_default"
              @change="toggleDefault(app.id)"
              class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-dark-700 dark:border-dark-600"
            />
            <label :for="`default-${app.id}`" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Make Default
            </label>
          </div>
          
          <div class="flex gap-2">
            <button
              @click="switchApp(app.id)"
              class="flex-1 btn-primary text-sm"
            >
              Switch to App
            </button>
            <button
              @click="editApp(app)"
              class="px-3 py-2 text-sm btn-secondary"
            >
              Edit
            </button>
            <button
              @click="deleteApp(app.id)"
              class="px-3 py-2 text-sm border border-danger-300 text-danger-600 rounded-lg hover:bg-danger-50 dark:border-danger-700 dark:text-danger-400 dark:hover:bg-danger-900 transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddModal || editingApp"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="card w-full max-w-md">
        <h2 class="text-2xl font-display font-bold mb-6 text-gray-900 dark:text-white">
          {{ editingApp ? 'Edit App' : 'Add New App' }}
        </h2>
        <form @submit.prevent="saveApp" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              App Name
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              placeholder="e.g., My Trading Account"
              class="input-field"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Client ID (Account ID)
            </label>
            <input
              v-model="formData.account_id"
              type="text"
              required
              placeholder="Your Angel One Client Code"
              class="input-field"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">Your Angel One Client Code</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              API Key
            </label>
            <input
              v-model="formData.api_key"
              type="password"
              required
              placeholder="SmartAPI API Key"
              class="input-field"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">From SmartAPI dashboard</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Secret Key
            </label>
            <input
              v-model="formData.secret_key"
              type="password"
              required
              placeholder="SmartAPI Secret Key"
              class="input-field"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">From SmartAPI dashboard</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              MPIN
            </label>
            <input
              v-model="formData.mpin"
              type="password"
              required
              placeholder="Angel One MPIN"
              maxlength="4"
              class="input-field"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">Your Angel One MPIN (4-digit Mobile Personal Identification Number)</p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Base URL
            </label>
            <input
              v-model="formData.base_url"
              type="text"
              required
              placeholder="https://apiconnect.angelbroking.com"
              class="input-field"
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">SmartAPI base URL (default: https://apiconnect.angelbroking.com)</p>
          </div>
          <div class="flex items-center">
            <input
              v-model="formData.is_default"
              type="checkbox"
              :id="'is-default-checkbox'"
              class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-dark-700 dark:border-dark-600"
            />
            <label :for="'is-default-checkbox'" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
              Set as Default App
            </label>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="submit"
              class="flex-1 btn-primary"
            >
              Save
            </button>
            <button
              type="button"
              @click="closeModal"
              class="flex-1 btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- OTP Modal -->
    <div
      v-if="showOtpModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeOtpModal"
    >
      <div class="card w-full max-w-md">
        <h2 class="text-2xl font-display font-bold mb-4 text-gray-900 dark:text-white">Enter OTP</h2>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          Please enter the 6-digit OTP from your authenticator app to switch to this app.
        </p>
        <form @submit.prevent="submitOtp" class="space-y-5">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              OTP (6 digits)
            </label>
            <input
              v-model="otpInput"
              type="text"
              required
              placeholder="000000"
              maxlength="6"
              pattern="[0-9]{6}"
              class="input-field text-center text-2xl tracking-widest font-mono"
              autofocus
            />
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1.5">Enter the 6-digit code from your authenticator app</p>
          </div>
          <div class="flex gap-3 pt-2">
            <button
              type="submit"
              class="flex-1 btn-primary"
            >
              Submit
            </button>
            <button
              type="button"
              @click="closeOtpModal"
              class="flex-1 btn-secondary"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store/app'
import apiClient from '../api/client'
import { showSuccess, showError, showInfo } from '../utils/toast'

export default {
  name: 'AppSelectorPage',
  setup() {
    const router = useRouter()
    const appStore = useAppStore()
    const loading = ref(false)
    const showAddModal = ref(false)
    const editingApp = ref(null)
    const showOtpModal = ref(false)
    const otpInput = ref('')
    const switchingAppId = ref(null)
    const formData = ref({
      name: '',
      account_id: '',
      api_key: '',
      secret_key: '',
      mpin: '',
      base_url: 'https://apiconnect.angelbroking.com',
      is_default: false
    })

    const apps = computed(() => appStore.apps)

    const loadApps = async () => {
      loading.value = true
      try {
        const response = await apiClient.get('/apps')
        appStore.setApps(response.data)
      } catch (error) {
        console.error('Failed to load apps:', error)
      } finally {
        loading.value = false
      }
    }

    const switchApp = async (appId) => {
      // Show OTP popup immediately
      switchingAppId.value = appId
      showOtpModal.value = true
    }

    const submitOtp = async () => {
      if (!otpInput.value || otpInput.value.length < 6) {
        showError('Please enter a valid 6-digit OTP')
        return
      }
      
      try {
        const response = await apiClient.post(`/apps/${switchingAppId.value}/switch`, { totp: otpInput.value })
        
        // Store session data
        if (response.data?.session) {
          appStore.setSession(response.data.session)
        }
        
        // Reload apps to get updated status
        await loadApps()
        
        // Find and set the active app after reloading
        const activeApp = apps.value.find(app => app.id === response.data.app_id)
        if (activeApp) {
          // Update status to active since we just switched to it
          const appWithActiveStatus = {
            ...activeApp,
            status: 'active'
          }
          appStore.setActiveApp(appWithActiveStatus)
        } else {
          // If app not found in list, try to find it from the store directly
          const storeApp = appStore.apps.find(app => app.id === response.data.app_id)
          if (storeApp) {
            const appWithActiveStatus = {
              ...storeApp,
              status: 'active'
            }
            appStore.setActiveApp(appWithActiveStatus)
          } else {
            console.warn('Active app not found in apps list')
          }
        }
        
        closeOtpModal()
        showSuccess('App switched successfully!')
        
        // Small delay to ensure state is updated before navigation
        setTimeout(() => {
          router.push('/dashboard')
        }, 100)
      } catch (error) {
        console.error('Failed to switch app with OTP:', error)
        const errorMsg = error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to switch app. Please check your OTP.'
        showError(errorMsg)
      }
    }

    const closeOtpModal = () => {
      showOtpModal.value = false
      otpInput.value = ''
      switchingAppId.value = null
    }

    const toggleDefault = async (appId) => {
      try {
        await apiClient.post(`/apps/${appId}/set-default`)
        await loadApps()
        showSuccess('Default app updated')
      } catch (error) {
        console.error('Failed to set default:', error)
        showError('Failed to set default app')
      }
    }

    const editApp = (app) => {
      editingApp.value = app
      formData.value = {
        name: app.name,
        account_id: app.account_id,
        api_key: '',  // Don't show existing credentials for security
        secret_key: '',
        mpin: '',
        base_url: app.base_url || 'https://apiconnect.angelbroking.com',
        is_default: app.is_default || false
      }
    }

    const deleteApp = async (appId) => {
      if (!confirm('Are you sure you want to delete this app?')) return
      
      try {
        await apiClient.delete(`/apps/${appId}`)
        appStore.removeApp(appId)
        showSuccess('App deleted successfully')
      } catch (error) {
        console.error('Failed to delete app:', error)
        showError(error.response?.data?.detail || 'Failed to delete app')
      }
    }

    const saveApp = async () => {
      try {
        if (editingApp.value) {
          await apiClient.put(`/apps/${editingApp.value.id}`, formData.value)
          showSuccess('App updated successfully')
        } else {
          await apiClient.post('/apps', formData.value)
          showSuccess('App created successfully')
        }
        await loadApps()
        closeModal()
      } catch (error) {
        console.error('Failed to save app:', error)
        showError(error.response?.data?.detail || 'Failed to save app')
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingApp.value = null
      formData.value = { 
        name: '', 
        account_id: '', 
        api_key: '', 
        secret_key: '', 
        mpin: '',
        base_url: 'https://apiconnect.angelbroking.com',
        is_default: false
      }
    }

    onMounted(() => {
      loadApps()
    })

    return {
      apps,
      loading,
      showAddModal,
      editingApp,
      formData,
      switchApp,
      toggleDefault,
      editApp,
      deleteApp,
      saveApp,
      closeModal,
      showOtpModal,
      otpInput,
      submitOtp,
      closeOtpModal
    }
  }
}
</script>

