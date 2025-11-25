<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <h1 class="text-3xl font-bold text-gray-900 mb-6">Settings</h1>
      
      <div class="bg-white rounded-lg shadow-md p-6 space-y-6">
        <div>
          <h2 class="text-xl font-semibold mb-4">Global Settings</h2>
          <div class="space-y-4">
            <div class="flex items-center">
              <input
                id="paper-mode"
                type="checkbox"
                v-model="settings.paper_mode"
                class="mr-2"
              />
              <label for="paper-mode" class="text-gray-700">
                Paper Trading Mode (simulate orders without executing)
              </label>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-1">
                Default Lot Size
              </label>
              <input
                v-model.number="settings.default_lot_size"
                type="number"
                min="1"
                class="w-full px-4 py-2 border border-gray-300 rounded-md"
              />
            </div>
          </div>
        </div>

        <div class="pt-4 border-t">
          <button
            @click="saveSettings"
            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
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
        alert('Settings saved successfully!')
      } catch (error) {
        console.error('Failed to save settings:', error)
        alert('Failed to save settings')
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

