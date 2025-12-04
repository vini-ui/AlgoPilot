<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white">Dashboard</h1>
        
        <!-- Funds Display -->
        <div v-if="fundsData && fundsData.status && fundsData.data" class="flex items-center gap-4">
          <div class="text-right">
            <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Available Funds</p>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              ₹{{ formatCurrency(fundsData.data.availablecash || fundsData.data.net || 0) }}
            </p>
          </div>
          <button
            @click="showFundsModal = true"
            class="px-3 py-1.5 text-xs font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
      
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
      
      <!-- User Profile Section -->
      <div v-if="userProfile && userProfile.status" class="card mb-6">
        <h2 class="text-xl font-display font-semibold text-gray-900 dark:text-white mb-4">User Profile</h2>
        <div v-if="userProfile.data" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Client Code</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userProfile.data.clientcode || 'N/A' }}</p>
            </div>
          </div>
          
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Name</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userProfile.data.name || 'N/A' }}</p>
            </div>
          </div>
          
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Email</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userProfile.data.email || 'Not provided' }}</p>
            </div>
          </div>
          
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Mobile</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userProfile.data.mobileno || 'Not provided' }}</p>
            </div>
          </div>
          
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Broker ID</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ userProfile.data.brokerid || 'N/A' }}</p>
            </div>
          </div>
          
          <div class="flex items-start gap-2">
            <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
            </svg>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 font-medium">Last Login</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatDate(userProfile.data.lastlogintime) }}</p>
            </div>
          </div>
        </div>
        
        <!-- Exchanges and Products -->
        <div v-if="userProfile.data" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-2">Exchanges</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="exchange in parseJsonArray(userProfile.data.exchanges)"
                :key="exchange"
                class="px-3 py-1 text-xs font-medium rounded-full bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200"
              >
                {{ formatExchange(exchange) }}
              </span>
            </div>
          </div>
          
          <div>
            <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-2">Products</p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="product in parseJsonArray(userProfile.data.products)"
                :key="product"
                class="px-3 py-1 text-xs font-medium rounded-full bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200"
              >
                {{ product }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <p class="text-gray-500 dark:text-gray-400 text-lg">Dashboard content coming soon...</p>
        <p class="text-gray-400 dark:text-gray-500 mt-2">This will show overall app statistics, active strategies, and recent activity.</p>
      </div>
    </div>
    
    <!-- Funds Modal -->
    <div
      v-if="showFundsModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="showFundsModal = false"
    >
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75" @click="showFundsModal = false"></div>
        
        <div class="inline-block align-bottom bg-white dark:bg-dark-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="px-6 py-4 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Funds Breakdown</h3>
            <button
              @click="showFundsModal = false"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <div class="px-6 py-4 max-h-96 overflow-y-auto">
            <div v-if="fundsData && fundsData.status && fundsData.data" class="space-y-4">
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Net Balance</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.net || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Available Cash</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.availablecash || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Available Intraday Payin</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.availableintradaypayin || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Available Limit Margin</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.availablelimitmargin || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Collateral</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.collateral || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">M2M Unrealized</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.m2munrealized || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">M2M Realized</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.m2mrealized || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Debits</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utiliseddebits || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Span</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedspan || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Option Premium</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedoptionpremium || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Holding Sales</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedholdingsales || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Exposure</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedexposure || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Turnover</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedturnover || 0) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Utilised Payout</p>
                  <p class="text-xl font-bold text-gray-900 dark:text-white">
                    ₹{{ formatCurrency(fundsData.data.utilisedpayout || 0) }}
                  </p>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <p class="text-gray-500 dark:text-gray-400">No funds data available</p>
            </div>
          </div>
          
          <div class="px-6 py-4 border-t border-gray-200 dark:border-dark-700 flex justify-end">
            <button
              @click="showFundsModal = false"
              class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useAppStore } from '../store/app'
import apiClient from '../api/client'
import { showError } from '../utils/toast'
import { getSession } from '../utils/session'

export default {
  name: 'DashboardPage',
  setup() {
    const appStore = useAppStore()
    const userProfile = ref(null)
    const loadingProfile = ref(false)
    const fundsData = ref(null)
    const loadingFunds = ref(false)
    const showFundsModal = ref(false)
    
    const activeApp = computed(() => appStore.activeApp)
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      try {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        return dateString
      }
    }

    const parseJsonArray = (data) => {
      if (!data) return []
      // If it's already an array, return it
      if (Array.isArray(data)) return data
      // If it's a string, try to parse it
      if (typeof data === 'string') {
        try {
          const parsed = JSON.parse(data)
          return Array.isArray(parsed) ? parsed : []
        } catch (e) {
          return []
        }
      }
      return []
    }

    const formatExchange = (exchange) => {
      if (!exchange) return ''
      // Replace underscores with spaces and convert to uppercase
      return exchange.replace(/_/g, ' ').toUpperCase()
    }

    const formatCurrency = (value) => {
      if (value === null || value === undefined) return '0.00'
      const numValue = typeof value === 'string' ? parseFloat(value) : value
      if (isNaN(numValue)) return '0.00'
      // Format with commas and 2 decimal places
      return numValue.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
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

    const loadUserProfile = async () => {
      if (!activeApp.value) {
        return
      }
      
      loadingProfile.value = true
      try {
        // Get session from store or localStorage
        const session = appStore.getSession() || getSession()
        
        // Use POST to send session data for restoration if we have it
        let response
        if (session && activeApp.value && session.access_token) {
          // Use POST to restore session
          response = await apiClient.post('/profile', {
            app_id: activeApp.value.id,
            session: session
          })
        } else {
          // Use GET if no session data
          response = await apiClient.get('/profile')
        }
        
        userProfile.value = response.data
      } catch (error) {
        console.error('Failed to load user profile:', error)
        // Don't show error if it's just because no active app
        if (error.response?.status !== 400) {
          showError('Failed to load user profile')
        }
      } finally {
        loadingProfile.value = false
      }
    }

    const loadFunds = async () => {
      if (!activeApp.value) {
        return
      }
      
      loadingFunds.value = true
      try {
        const response = await apiClient.get('/profile/funds')
        fundsData.value = response.data
      } catch (error) {
        console.error('Failed to load funds:', error)
        // Don't show error if it's just because no active app or session
        if (error.response?.status !== 400) {
          // Silently fail for funds - it's not critical
        }
      } finally {
        loadingFunds.value = false
      }
    }
    
    onMounted(async () => {
      // Load apps on mount to ensure we have fresh data
      await loadApps()
      
      // Load user profile and funds if we have an active app
      if (activeApp.value) {
        await Promise.all([
          loadUserProfile(),
          loadFunds()
        ])
      }
    })
    
    return {
      activeApp,
      userProfile,
      loadingProfile,
      fundsData,
      loadingFunds,
      showFundsModal,
      formatDate,
      parseJsonArray,
      formatExchange,
      formatCurrency
    }
  }
}
</script>

