<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-8">Settings</h1>
      
      <div class="card space-y-6">
        <div>
          <h2 class="text-xl font-display font-semibold mb-6 text-gray-900 dark:text-white">Global Settings</h2>
          <div class="space-y-5">
            <div class="flex items-center">
              <input
                id="paper-mode"
                type="checkbox"
                v-model="settings.paper_mode"
                class="w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-dark-700 dark:border-dark-600"
              />
              <label for="paper-mode" class="ml-2 text-sm font-medium text-gray-700 dark:text-gray-300">
                Paper Trading Mode (simulate orders without executing)
              </label>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Default Lot Size
              </label>
              <input
                v-model.number="settings.default_lot_size"
                type="number"
                min="1"
                class="input-field"
              />
            </div>
          </div>
        </div>

        <div class="pt-6 border-t border-gray-200 dark:border-dark-700">
          <button
            @click="saveSettings"
            class="btn-primary"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiClient from '../api/client'
import { showSuccess, showError } from '../utils/toast'

export default {
  name: 'SettingsPage',
  setup() {
    const settings = ref({
      paper_mode: false,
      default_lot_size: 1
    })

    const loadSettings = async () => {
      try {
        const response = await apiClient.get('/settings')
        settings.value = response.data
      } catch (error) {
        console.error('Failed to load settings:', error)
      }
    }

    const saveSettings = async () => {
      try {
        await apiClient.put('/settings', settings.value)
        showSuccess('Settings saved successfully!')
      } catch (error) {
        console.error('Failed to save settings:', error)
        showError('Failed to save settings')
      }
    }

    onMounted(() => {
      loadSettings()
    })

    return {
      settings,
      saveSettings
    }
  }
}
</script>

