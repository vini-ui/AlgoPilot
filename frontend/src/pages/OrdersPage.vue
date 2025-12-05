<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-9xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white">Orders</h1>
        <button
          @click="refreshOrders"
          :disabled="loading"
          class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <svg
            class="w-4 h-4"
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

      <!-- Filters -->
      <div class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-4 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <!-- Search by Symbol -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search Symbol
            </label>
            <input
              v-model="filters.symbol"
              type="text"
              placeholder="Enter symbol..."
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <!-- Filter by Status -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Status
            </label>
            <select
              v-model="filters.status"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Status</option>
              <option value="open">Open</option>
              <option value="complete">Complete</option>
              <option value="cancelled">Cancelled</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>

          <!-- Filter by Order Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Order Type
            </label>
            <select
              v-model="filters.orderType"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Types</option>
              <option value="MARKET">Market</option>
              <option value="LIMIT">Limit</option>
              <option value="STOPLOSS_LIMIT">Stop Loss Limit</option>
              <option value="STOPLOSS_MARKET">Stop Loss Market</option>
            </select>
          </div>

          <!-- Filter by Transaction Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Transaction Type
            </label>
            <select
              v-model="filters.transactionType"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All</option>
              <option value="BUY">Buy</option>
              <option value="SELL">Sell</option>
            </select>
          </div>
        </div>

        <!-- Clear Filters Button -->
        <div class="mt-4 flex justify-end">
          <button
            @click="clearFilters"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors"
          >
            Clear Filters
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading && !orders.length" class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading orders...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <svg class="mx-auto h-12 w-12 text-red-500 dark:text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="text-sm font-medium text-red-600 dark:text-red-400 mb-2">{{ error }}</p>
        <p v-if="error.includes('session') || error.includes('Switch')" class="text-xs text-gray-500 dark:text-gray-400 mb-4">
          You need to switch to an app and establish a session to view orders.
        </p>
        <div class="flex gap-3 justify-center">
          <button
            v-if="error.includes('session') || error.includes('Switch')"
            @click="$router.push('/apps')"
            class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md transition-colors"
          >
            Go to Apps
          </button>
          <button
            @click="refreshOrders"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors"
          >
            Retry
          </button>
        </div>
      </div>

      <!-- Orders Table -->
      <div v-else class="bg-white dark:bg-dark-800 rounded-xl shadow-md overflow-hidden">
        <div class="relative overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-dark-700 dark:text-gray-400">
              <tr>
                <th scope="col" class="px-6 py-3">Order ID</th>
                <th scope="col" class="px-6 py-3">Symbol</th>
                <th scope="col" class="px-6 py-3">Exchange</th>
                <th scope="col" class="px-6 py-3">Transaction</th>
                <th scope="col" class="px-6 py-3">Order Type</th>
                <th scope="col" class="px-6 py-3">Product</th>
                <th scope="col" class="px-6 py-3">Quantity/Lots</th>
                <th scope="col" class="px-6 py-3">Price</th>
                <th scope="col" class="px-6 py-3">Status</th>
                <th scope="col" class="px-6 py-3">Time</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(order, index) in filteredOrders"
                :key="order.orderid || index"
                @click="openOrderDetails(order)"
                class="bg-white border-b dark:bg-dark-800 dark:border-dark-700 hover:bg-gray-50 dark:hover:bg-dark-700 cursor-pointer transition-colors"
                :class="{ 'bg-gray-50 dark:bg-dark-700': index % 2 === 0 }"
              >
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">
                  {{ order.orderid || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ order.tradingsymbol || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ order.exchange || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      order.transactiontype === 'BUY'
                        ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
                        : 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200'
                    ]"
                  >
                    {{ order.transactiontype || 'N/A' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ order.ordertype || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ order.producttype || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ formatQuantity(order) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  ₹{{ formatPrice(order.averageprice || order.price || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      getStatusClass(order.status)
                    ]"
                  >
                    {{ order.status || 'N/A' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ formatTime(order.updatetime || order.time || order.exchangetime) }}
                </td>
              </tr>
              <tr v-if="filteredOrders.length === 0">
                <td colspan="10" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  <p class="mb-2">No orders found</p>
                  <p class="text-sm" v-if="hasActiveFilters">Try adjusting your filters</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Summary -->
        <div v-if="filteredOrders.length > 0" class="px-6 py-4 bg-gray-50 dark:bg-dark-700 border-t border-gray-200 dark:border-dark-600">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Showing <span class="font-medium">{{ filteredOrders.length }}</span> of
            <span class="font-medium">{{ orders.length }}</span> orders
          </p>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 z-50 overflow-y-auto"
      @click.self="closeModal"
    >
      <div class="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75 dark:bg-gray-900 dark:bg-opacity-75" @click="closeModal"></div>
        
        <div class="inline-block align-bottom bg-white dark:bg-dark-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <!-- Modal Header -->
          <div class="px-6 py-4 border-b border-gray-200 dark:border-dark-700 flex items-center justify-between">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Order Details</h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
          
          <!-- Modal Body -->
          <div class="px-6 py-4 max-h-96 overflow-y-auto">
            <div v-if="loadingDetails" class="text-center py-8">
              <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading order details...</p>
            </div>
            
            <div v-else-if="orderDetailsError" class="text-center py-8">
              <p class="text-sm text-red-600 dark:text-red-400">{{ orderDetailsError }}</p>
            </div>
            
            <div v-else-if="orderDetails" class="space-y-4">
              <!-- Order Information Grid -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Order ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.orderid || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Symbol</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.tradingsymbol || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Exchange</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.exchange || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Status</p>
                  <span
                    :class="[
                      'inline-block px-2 py-1 text-xs font-medium rounded-full',
                      getStatusClass(orderDetails.status || orderDetails.orderstatus)
                    ]"
                  >
                    {{ orderDetails.status || orderDetails.orderstatus || 'N/A' }}
                  </span>
                </div>
                
                <div v-if="orderDetails.orderstatus && orderDetails.orderstatus !== orderDetails.status" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Order Status</p>
                  <span
                    :class="[
                      'inline-block px-2 py-1 text-xs font-medium rounded-full',
                      getStatusClass(orderDetails.orderstatus)
                    ]"
                  >
                    {{ orderDetails.orderstatus }}
                  </span>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Transaction Type</p>
                  <span
                    :class="[
                      'inline-block px-2 py-1 text-xs font-medium rounded-full',
                      orderDetails.transactiontype === 'BUY'
                        ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
                        : 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200'
                    ]"
                  >
                    {{ orderDetails.transactiontype || 'N/A' }}
                  </span>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Order Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.ordertype || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Product Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.producttype || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Variety</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.variety || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.quantity || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.price || orderDetails.averageprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Trigger Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.triggerprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Disclosed Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.disclosedquantity || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Duration</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.duration || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Filled Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.filledshares || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Unfilled Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.unfilledshares || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Order Time</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatTime(orderDetails.updatetime || orderDetails.time || orderDetails.exchangetime) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Exchange Time</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatTime(orderDetails.exchangetime || orderDetails.updatetime) }}</p>
                </div>
              </div>
              
              <!-- Additional Details -->
              <div v-if="orderDetails.symboltoken" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Symbol Token</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.symboltoken }}</p>
              </div>
              
                <div v-if="orderDetails.uniqueorderid" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Unique Order ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.uniqueorderid }}</p>
                </div>
                
                <div v-if="orderDetails.exchangeorderid" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Exchange Order ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.exchangeorderid }}</p>
                </div>
                
                <div v-if="orderDetails.parentorderid" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Parent Order ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.parentorderid }}</p>
                </div>
                
                <div v-if="orderDetails.ordertag" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Order Tag</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.ordertag || 'N/A' }}</p>
                </div>
                
                <div v-if="orderDetails.fillid" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Fill ID</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.fillid }}</p>
                </div>
                
                <div v-if="orderDetails.filltime" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Fill Time</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatTime(orderDetails.filltime) }}</p>
                </div>
                
                <div v-if="orderDetails.exchorderupdatetime" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Exchange Order Update Time</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ formatTime(orderDetails.exchorderupdatetime) }}</p>
                </div>
                
                <div v-if="orderDetails.stoploss" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Stop Loss</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.stoploss) }}</p>
                </div>
                
                <div v-if="orderDetails.trailingstoploss" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Trailing Stop Loss</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.trailingstoploss) }}</p>
                </div>
                
                <div v-if="orderDetails.squareoff" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Square Off</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.squareoff) }}</p>
                </div>
                
                <div v-if="orderDetails.cancelsize" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Cancel Size</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.cancelsize }}</p>
                </div>
                
                <div v-if="orderDetails.lotsize" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Lot Size</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.lotsize }}</p>
                </div>
                
                <div v-if="orderDetails.instrumenttype" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Instrument Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.instrumenttype }}</p>
                </div>
                
                <div v-if="orderDetails.strikeprice && orderDetails.strikeprice !== '-1' && orderDetails.strikeprice !== -1" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Strike Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(orderDetails.strikeprice) }}</p>
                </div>
                
                <div v-if="orderDetails.optiontype" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Option Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.optiontype }}</p>
                </div>
                
                <div v-if="orderDetails.expirydate" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Expiry Date</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ orderDetails.expirydate }}</p>
                </div>
                
                <div v-if="orderDetails.text" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg col-span-1 md:col-span-2">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Message/Text</p>
                  <p class="text-sm text-gray-900 dark:text-white">{{ orderDetails.text }}</p>
                </div>
            </div>
          </div>
          
          <!-- Modal Footer -->
          <div class="px-6 py-4 border-t border-gray-200 dark:border-dark-700 flex justify-end">
            <button
              @click="closeModal"
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
import { ref, computed, onMounted } from 'vue'
import apiClient from '../api/client'

export default {
  name: 'OrdersPage',
  setup() {
    const orders = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showModal = ref(false)
    const orderDetails = ref(null)
    const loadingDetails = ref(false)
    const orderDetailsError = ref(null)

    const filters = ref({
      symbol: '',
      status: '',
      orderType: '',
      transactionType: ''
    })

    const filteredOrders = computed(() => {
      let result = [...orders.value]

      // Filter by symbol
      if (filters.value.symbol) {
        const symbolLower = filters.value.symbol.toLowerCase()
        result = result.filter(order =>
          (order.tradingsymbol || '').toLowerCase().includes(symbolLower)
        )
      }

      // Filter by status
      if (filters.value.status) {
        const statusLower = filters.value.status.toLowerCase()
        result = result.filter(order =>
          (order.status || '').toLowerCase() === statusLower
        )
      }

      // Filter by order type
      if (filters.value.orderType) {
        result = result.filter(order =>
          order.ordertype === filters.value.orderType
        )
      }

      // Filter by transaction type
      if (filters.value.transactionType) {
        result = result.filter(order =>
          order.transactiontype === filters.value.transactionType
        )
      }

      // Sort by time (newest first)
      result.sort((a, b) => {
        const getTime = (order) => {
          // Try updatetime first, then time, then exchangetime
          const timeStr = order.updatetime || order.time || order.exchangetime || order.exchorderupdatetime || order.filltime
          if (!timeStr) return 0
          try {
            return new Date(timeStr).getTime()
          } catch (e) {
            return 0
          }
        }
        
        const timeA = getTime(a)
        const timeB = getTime(b)
        
        // Sort descending (newest first)
        return timeB - timeA
      })

      return result
    })

    const hasActiveFilters = computed(() => {
      return !!(
        filters.value.symbol ||
        filters.value.status ||
        filters.value.orderType ||
        filters.value.transactionType
      )
    })

    const formatPrice = (price) => {
      if (!price || price === '0' || price === 0) return '0.00'
      const numPrice = typeof price === 'string' ? parseFloat(price) : price
      if (isNaN(numPrice)) return '0.00'
      return numPrice.toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
    }

    const formatQuantity = (order) => {
      const quantity = order.quantity || '0'
      const lotsize = order.lotsize
      
      if (lotsize && lotsize !== '0' && lotsize !== 0) {
        const qty = parseFloat(quantity) || 0
        const lotSize = parseFloat(lotsize) || 1
        const lots = lotSize > 0 ? Math.floor(qty / lotSize) : '0'
        return `${quantity} (${lots} lots)`
      }
      
      return quantity
    }

    const formatTime = (timeString) => {
      if (!timeString) return 'N/A'
      try {
        const date = new Date(timeString)
        return date.toLocaleString('en-IN', {
          day: '2-digit',
          month: 'short',
          year: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        })
      } catch (e) {
        return timeString
      }
    }

    const getStatusClass = (status) => {
      if (!status) return 'bg-gray-100 text-gray-800 dark:bg-dark-600 dark:text-gray-300'
      
      const statusLower = status.toLowerCase()
      if (statusLower === 'complete' || statusLower === 'filled') {
        return 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
      } else if (statusLower === 'cancelled' || statusLower === 'cancel') {
        return 'bg-gray-100 text-gray-800 dark:bg-dark-600 dark:text-gray-300'
      } else if (statusLower === 'rejected' || statusLower === 'reject') {
        return 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200'
      } else if (statusLower === 'open' || statusLower === 'pending' || statusLower === 'trigger pending') {
        return 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-200'
      }
      return 'bg-gray-100 text-gray-800 dark:bg-dark-600 dark:text-gray-300'
    }

    const fetchOrders = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await apiClient.get('/orders')
        
        if (response.data && response.data.status && response.data.data) {
          orders.value = Array.isArray(response.data.data) ? response.data.data : []
        } else if (Array.isArray(response.data)) {
          // Fallback if response is directly an array
          orders.value = response.data
        } else {
          orders.value = []
        }
      } catch (err) {
        console.error('Failed to fetch orders:', err)
        error.value = err.response?.data?.detail || err.message || 'Failed to fetch orders'
        orders.value = []
      } finally {
        loading.value = false
      }
    }

    const refreshOrders = () => {
      fetchOrders()
    }

    const clearFilters = () => {
      filters.value = {
        symbol: '',
        status: '',
        orderType: '',
        transactionType: ''
      }
    }

    const openOrderDetails = async (order) => {
      if (!order.orderid) {
        return
      }
      
      showModal.value = true
      orderDetails.value = null
      orderDetailsError.value = null
      loadingDetails.value = true
      
      try {
        const response = await apiClient.get(`/orders/${order.orderid}`)
        
        if (response.data && response.data.status && response.data.data) {
          orderDetails.value = response.data.data
        } else {
          orderDetailsError.value = 'Failed to load order details'
        }
      } catch (err) {
        console.error('Failed to fetch order details:', err)
        orderDetailsError.value = err.response?.data?.detail || err.message || 'Failed to fetch order details'
      } finally {
        loadingDetails.value = false
      }
    }

    const closeModal = () => {
      showModal.value = false
      orderDetails.value = null
      orderDetailsError.value = null
    }

    onMounted(() => {
      fetchOrders()
    })

    return {
      orders,
      loading,
      error,
      filters,
      filteredOrders,
      hasActiveFilters,
      formatPrice,
      formatQuantity,
      formatTime,
      getStatusClass,
      refreshOrders,
      clearFilters,
      showModal,
      orderDetails,
      loadingDetails,
      orderDetailsError,
      openOrderDetails,
      closeModal
    }
  }
}
</script>
