<template>
  <div class="card">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-display font-semibold text-gray-900 dark:text-white">
        Top Gainers & Losers
      </h2>
      <button
        @click="refreshData"
        :disabled="loading"
        class="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg
          class="w-4 h-4 inline mr-1"
          :class="{ 'animate-spin': loading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          ></path>
        </svg>
        Refresh
      </button>
    </div>

    <div v-if="loading && !data" class="text-center py-8">
      <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading market data...</p>
    </div>

    <div v-else-if="error" class="text-center py-8">
      <p class="text-sm text-red-600 dark:text-red-400">{{ error }}</p>
      <button
        @click="refreshData"
        class="mt-4 px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
      >
        Retry
      </button>
    </div>

    <div v-else-if="data" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Top Gainers -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Top Gainers</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-dark-700">
            <thead class="bg-gray-50 dark:bg-dark-700">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Symbol
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Change %
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  OI
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Net OI Change
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-dark-800 divide-y divide-gray-200 dark:divide-dark-700">
              <tr
                v-for="(stock, index) in data.gainers"
                :key="`gainer-${index}`"
                class="hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
              >
                <td class="px-3 py-2 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ stock.symbol }}
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm font-medium text-success-600">
                    +{{ stock.percentChange }}%
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ formatNumber(stock.opnInterest) }}
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    {{ formatNumber(stock.netChangeOpnInterest) }}
                  </div>
                </td>
              </tr>
              <tr v-if="!data.gainers || data.gainers.length === 0">
                <td colspan="4" class="px-3 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No gainers data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Top Losers -->
      <div>
        <div class="flex items-center gap-2 mb-3">
          <svg class="w-5 h-5 text-danger-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6"></path>
          </svg>
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Top Losers</h3>
        </div>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-dark-700">
            <thead class="bg-gray-50 dark:bg-dark-700">
              <tr>
                <th class="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Symbol
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Change %
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  OI
                </th>
                <th class="px-3 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Net OI Change
                </th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-dark-800 divide-y divide-gray-200 dark:divide-dark-700">
              <tr
                v-for="(stock, index) in data.losers"
                :key="`loser-${index}`"
                class="hover:bg-gray-50 dark:hover:bg-dark-700 transition-colors"
              >
                <td class="px-3 py-2 whitespace-nowrap">
                  <div class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ stock.symbol }}
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm font-medium text-danger-600">
                    {{ stock.percentChange }}%
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm text-gray-900 dark:text-white">
                    {{ formatNumber(stock.opnInterest) }}
                  </div>
                </td>
                <td class="px-3 py-2 whitespace-nowrap text-right">
                  <div class="text-sm text-gray-600 dark:text-gray-400">
                    {{ formatNumber(stock.netChangeOpnInterest) }}
                  </div>
                </td>
              </tr>
              <tr v-if="!data.losers || data.losers.length === 0">
                <td colspan="4" class="px-3 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                  No losers data available
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-8">
      <p class="text-sm text-gray-500 dark:text-gray-400">No data available</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import apiClient from '../api/client'
import { showError } from '../utils/toast'

export default {
  name: 'TopGainersLosers',
  setup() {
    const data = ref(null)
    const loading = ref(false)
    const error = ref(null)

    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '0.00'
      const numValue = typeof value === 'string' ? parseFloat(value) : value
      if (isNaN(numValue)) return '0.00'
      return numValue.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    const formatNumber = (value) => {
      if (value === null || value === undefined) return '0'
      const numValue = typeof value === 'string' ? parseFloat(value) : value
      if (isNaN(numValue)) return '0'
      // Format large numbers with K, M, B suffixes
      if (numValue >= 1000000000) {
        return (numValue / 1000000000).toFixed(2) + 'B'
      } else if (numValue >= 1000000) {
        return (numValue / 1000000).toFixed(2) + 'M'
      } else if (numValue >= 1000) {
        return (numValue / 1000).toFixed(2) + 'K'
      }
      return numValue.toLocaleString('en-IN', {
        maximumFractionDigits: 0
      })
    }

    const fetchData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await apiClient.get('/profile/market/gainers-losers', {
          params: {
            datatype: 'PercPriceGainers',
            expirytype: 'NEAR',
            limit: 20
          }
        })
        
        if (response.data && response.data.status && response.data.data) {
          data.value = response.data.data
        } else {
          error.value = 'Failed to fetch market data'
        }
      } catch (err) {
        console.error('Failed to fetch top gainers/losers:', err)
        console.error('Error response:', err.response)
        // Try to get the error message from different possible locations
        const errorMsg = err.response?.data?.detail || 
                        err.response?.data?.message || 
                        err.message || 
                        'Failed to fetch market data'
        error.value = errorMsg
        console.error('Error message:', errorMsg)
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      fetchData()
    }

    onMounted(() => {
      fetchData()
    })

    return {
      data,
      loading,
      error,
      formatCurrency,
      formatNumber,
      refreshData
    }
  }
}
</script>

