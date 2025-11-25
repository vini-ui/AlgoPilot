<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">Strategies</h1>
        <div class="flex gap-2">
          <button
            @click="startAll"
            class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
          >
            Start All
          </button>
          <button
            @click="stopAll"
            class="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
          >
            Stop All
          </button>
          <button
            @click="showAddModal = true"
            class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
          >
            Add Strategy
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading strategies...</p>
      </div>

      <div v-else-if="strategies.length === 0" class="text-center py-12">
        <p class="text-gray-500 mb-4">No strategies configured yet.</p>
        <button
          @click="showAddModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Create Your First Strategy
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="strategy in strategies"
          :key="strategy.id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
        >
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-semibold text-gray-900">{{ strategy.name }}</h3>
            <span
              :class="[
                'px-2 py-1 text-xs rounded-full',
                strategy.status === 'running' ? 'bg-green-100 text-green-800' :
                strategy.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                'bg-gray-100 text-gray-800'
              ]"
            >
              {{ strategy.status || 'stopped' }}
            </span>
          </div>
          
          <p class="text-gray-600 mb-2">Type: {{ strategy.type }}</p>
          <p class="text-sm text-gray-500 mb-4">Created: {{ new Date(strategy.created_at).toLocaleDateString() }}</p>
          
          <div class="flex gap-2">
            <button
              @click="startStrategy(strategy.id)"
              class="flex-1 bg-green-600 text-white px-3 py-2 rounded-md text-sm hover:bg-green-700"
            >
              Start
            </button>
            <button
              @click="stopStrategy(strategy.id)"
              class="flex-1 bg-red-600 text-white px-3 py-2 rounded-md text-sm hover:bg-red-700"
            >
              Stop
            </button>
            <button
              @click="viewStrategy(strategy.id)"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
            >
              View
            </button>
            <button
              @click="deleteStrategy(strategy.id)"
              class="px-3 py-2 border border-red-300 text-red-600 rounded-md text-sm hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStrategyStore } from '../store/strategy'
import apiClient from '../api/client'

export default {
  name: 'StrategyListPage',
  setup() {
    const router = useRouter()
    const strategyStore = useStrategyStore()
    const loading = ref(false)
    const showAddModal = ref(false)

    const strategies = computed(() => strategyStore.strategies)

    const loadStrategies = async () => {
      loading.value = true
      try {
        const response = await apiClient.get('/strategies')
        strategyStore.setStrategies(response.data)
      } catch (error) {
        console.error('Failed to load strategies:', error)
      } finally {
        loading.value = false
      }
    }

    const startStrategy = async (id) => {
      try {
        await apiClient.post(`/strategies/${id}/start`)
        await loadStrategies()
      } catch (error) {
        console.error('Failed to start strategy:', error)
      }
    }

    const stopStrategy = async (id) => {
      try {
        await apiClient.post(`/strategies/${id}/stop`)
        await loadStrategies()
      } catch (error) {
        console.error('Failed to stop strategy:', error)
      }
    }

    const startAll = async () => {
      try {
        await apiClient.post('/strategies/start-all')
        await loadStrategies()
      } catch (error) {
        console.error('Failed to start all strategies:', error)
      }
    }

    const stopAll = async () => {
      try {
        await apiClient.post('/strategies/stop-all')
        await loadStrategies()
      } catch (error) {
        console.error('Failed to stop all strategies:', error)
      }
    }

    const viewStrategy = (id) => {
      router.push(`/strategies/${id}`)
    }

    const deleteStrategy = async (id) => {
      if (!confirm('Are you sure you want to delete this strategy?')) return
      
      try {
        await apiClient.delete(`/strategies/${id}`)
        strategyStore.removeStrategy(id)
      } catch (error) {
        console.error('Failed to delete strategy:', error)
      }
    }

    onMounted(() => {
      loadStrategies()
    })

    return {
      strategies,
      loading,
      showAddModal,
      startStrategy,
      stopStrategy,
      startAll,
      stopAll,
      viewStrategy,
      deleteStrategy
    }
  }
}
</script>

