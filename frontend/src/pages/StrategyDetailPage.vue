<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">
          Strategy: {{ strategy?.name || 'Loading...' }}
        </h1>
        <div class="flex gap-2">
          <button
            @click="runNow"
            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Run Now
          </button>
          <button
            @click="startStrategy"
            class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Start
          </button>
          <button
            @click="pauseStrategy"
            class="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
          >
            Pause
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading strategy details...</p>
      </div>

      <div v-else-if="strategy" class="space-y-6">
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">Parameters</h2>
          <pre class="bg-gray-50 p-4 rounded-md overflow-auto">{{ JSON.stringify(JSON.parse(strategy.params_json || '{}'), null, 2) }}</pre>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold mb-4">Logs</h2>
          <div class="bg-gray-900 text-green-400 p-4 rounded-md font-mono text-sm h-64 overflow-auto">
            <div v-for="(log, index) in logs" :key="index" class="mb-1">
              {{ log }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '../api/client'

export default {
  name: 'StrategyDetailPage',
  setup() {
    const route = useRoute()
    const loading = ref(false)
    const strategy = ref(null)
    const logs = ref([])

    const loadStrategy = async () => {
      loading.value = true
      try {
        const response = await apiClient.get(`/strategies/${route.params.id}`)
        strategy.value = response.data
      } catch (error) {
        console.error('Failed to load strategy:', error)
      } finally {
        loading.value = false
      }
    }

    const runNow = async () => {
      try {
        await apiClient.post(`/strategies/${route.params.id}/run-now`)
        logs.value.push(`[${new Date().toLocaleTimeString()}] Strategy executed`)
      } catch (error) {
        console.error('Failed to run strategy:', error)
      }
    }

    const startStrategy = async () => {
      try {
        await apiClient.post(`/strategies/${route.params.id}/start`)
        await loadStrategy()
      } catch (error) {
        console.error('Failed to start strategy:', error)
      }
    }

    const pauseStrategy = async () => {
      try {
        await apiClient.post(`/strategies/${route.params.id}/pause`)
        await loadStrategy()
      } catch (error) {
        console.error('Failed to pause strategy:', error)
      }
    }

    onMounted(() => {
      loadStrategy()
    })

    return {
      strategy,
      loading,
      logs,
      runNow,
      startStrategy,
      pauseStrategy
    }
  }
}
</script>

