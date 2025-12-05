<template>
  <div class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between mb-6 gap-4">
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white">Positions</h1>
        <button
          @click="refreshPositions"
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

          <!-- Filter by Exchange -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Exchange
            </label>
            <select
              v-model="filters.exchange"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Exchanges</option>
              <option value="NSE">NSE</option>
              <option value="BSE">BSE</option>
              <option value="NFO">NFO</option>
              <option value="MCX">MCX</option>
            </select>
          </div>

          <!-- Filter by Product Type -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Product Type
            </label>
            <select
              v-model="filters.productType"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Products</option>
              <option value="INTRADAY">Intraday</option>
              <option value="DELIVERY">Delivery</option>
              <option value="MARGIN">Margin</option>
            </select>
          </div>

          <!-- Filter by Net Qty -->
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Net Quantity
            </label>
            <select
              v-model="filters.netQty"
              class="w-full px-3 py-2 text-sm border border-gray-300 dark:border-dark-600 rounded-md bg-white dark:bg-dark-700 text-gray-900 dark:text-white focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All</option>
              <option value="positive">Positive (Long)</option>
              <option value="negative">Negative (Short)</option>
              <option value="zero">Zero</option>
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
      <div v-if="loading && !positions.length" class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">Loading positions...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-white dark:bg-dark-800 rounded-xl shadow-md p-8 text-center">
        <svg class="mx-auto h-12 w-12 text-red-500 dark:text-red-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <p class="text-sm font-medium text-red-600 dark:text-red-400 mb-2">{{ error }}</p>
        <p v-if="error.includes('session') || error.includes('Switch')" class="text-xs text-gray-500 dark:text-gray-400 mb-4">
          You need to switch to an app and establish a session to view positions.
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
            @click="refreshPositions"
            class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-dark-700 hover:bg-gray-200 dark:hover:bg-dark-600 rounded-md transition-colors"
          >
            Retry
          </button>
        </div>
      </div>

      <!-- Positions Table -->
      <div v-else class="bg-white dark:bg-dark-800 rounded-xl shadow-md overflow-hidden">
        <div class="relative overflow-x-auto">
          <table class="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-dark-700 dark:text-gray-400">
              <tr>
                <th scope="col" class="px-6 py-3">Symbol</th>
                <th scope="col" class="px-6 py-3">Exchange</th>
                <th scope="col" class="px-6 py-3">Product</th>
                <th scope="col" class="px-6 py-3">Net Qty</th>
                <th scope="col" class="px-6 py-3">Buy Qty</th>
                <th scope="col" class="px-6 py-3">Sell Qty</th>
                <th scope="col" class="px-6 py-3">Avg Price</th>
                <th scope="col" class="px-6 py-3">Net Value</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(position, index) in filteredPositions"
                :key="position.symboltoken || index"
                @click="openPositionDetails(position)"
                class="bg-white border-b dark:bg-dark-800 dark:border-dark-700 hover:bg-gray-50 dark:hover:bg-dark-700 cursor-pointer transition-colors"
                :class="{ 'bg-gray-50 dark:bg-dark-700': index % 2 === 0 }"
              >
                <td class="px-6 py-4 font-medium text-gray-900 dark:text-white whitespace-nowrap">
                  {{ position.tradingsymbol || position.symbolname || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ position.exchange || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ position.producttype || 'N/A' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-medium rounded-full',
                      parseFloat(position.netqty || 0) > 0
                        ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
                        : parseFloat(position.netqty || 0) < 0
                        ? 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-dark-600 dark:text-gray-300'
                    ]"
                  >
                    {{ position.netqty || '0' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ position.buyqty || '0' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  {{ position.sellqty || '0' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  ₹{{ formatPrice(position.avgnetprice || position.netprice || 0) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="[
                      'font-medium',
                      parseFloat(String(position.netvalue || 0).replace('- ', '').replace('-', '')) >= 0
                        ? 'text-success-600 dark:text-success-400'
                        : 'text-danger-600 dark:text-danger-400'
                    ]"
                  >
                    {{ formatNetValue(position.netvalue) }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredPositions.length === 0">
                <td colspan="9" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                  <p class="mb-2">No positions found</p>
                  <p class="text-sm" v-if="hasActiveFilters">Try adjusting your filters</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Summary -->
        <div v-if="filteredPositions.length > 0" class="px-6 py-4 bg-gray-50 dark:bg-dark-700 border-t border-gray-200 dark:border-dark-600">
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Positions</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ filteredPositions.length }}</p>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Net Value</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ formatNetValue(calculateTotalNetValue()) }}
              </p>
            </div>
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Total Positions Value</p>
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ filteredPositions.length }} positions
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Position Details Modal -->
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
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Position Details</h3>
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
            <div v-if="positionDetails" class="space-y-4">
              <!-- Position Information Grid -->
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Symbol</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.tradingsymbol || positionDetails.symbolname || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Exchange</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.exchange || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Product Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.producttype || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Symbol Token</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.symboltoken || 'N/A' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Net Quantity</p>
                  <span
                    :class="[
                      'inline-block px-2 py-1 text-xs font-medium rounded-full',
                      parseFloat(positionDetails.netqty || 0) > 0
                        ? 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-200'
                        : parseFloat(positionDetails.netqty || 0) < 0
                        ? 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-200'
                        : 'bg-gray-100 text-gray-800 dark:bg-dark-600 dark:text-gray-300'
                    ]"
                  >
                    {{ positionDetails.netqty || '0' }}
                  </span>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Net Value</p>
                  <p
                    class="text-sm font-semibold"
                    :class="[
                      parseFloat(positionDetails.netvalue || 0) >= 0
                        ? 'text-success-600 dark:text-success-400'
                        : 'text-danger-600 dark:text-danger-400'
                    ]"
                  >
                    {{ formatNetValue(positionDetails.netvalue) }}
                  </p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Buy Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.buyqty || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Sell Quantity</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.sellqty || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Buy Amount</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.buyamount || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Sell Amount</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.sellamount || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Buy Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.buyavgprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Sell Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.sellavgprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Average Net Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.avgnetprice || positionDetails.netprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Net Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.netprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Total Buy Value</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.totalbuyvalue || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Total Sell Value</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.totalsellvalue || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Buy Qty</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.cfbuyqty || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Sell Qty</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.cfsellqty || '0' }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Buy Amount</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.cfbuyamount || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Sell Amount</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.cfsellamount || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Buy Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.cfbuyavgprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">CF Sell Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.cfsellavgprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Total Buy Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.totalbuyavgprice || 0) }}</p>
                </div>
                
                <div class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Total Sell Avg Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.totalsellavgprice || 0) }}</p>
                </div>
                
                <div v-if="positionDetails.lotsize" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Lot Size</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.lotsize }}</p>
                </div>
                
                <div v-if="positionDetails.boardlotsize" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Board Lot Size</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.boardlotsize }}</p>
                </div>
                
                <div v-if="positionDetails.instrumenttype" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Instrument Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.instrumenttype }}</p>
                </div>
                
                <div v-if="positionDetails.strikeprice && positionDetails.strikeprice !== '-1' && positionDetails.strikeprice !== -1" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Strike Price</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">₹{{ formatPrice(positionDetails.strikeprice) }}</p>
                </div>
                
                <div v-if="positionDetails.optiontype" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Option Type</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.optiontype }}</p>
                </div>
                
                <div v-if="positionDetails.expirydate" class="p-4 bg-gray-50 dark:bg-dark-700 rounded-lg">
                  <p class="text-xs text-gray-500 dark:text-gray-400 font-medium mb-1">Expiry Date</p>
                  <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ positionDetails.expirydate }}</p>
                </div>
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
  name: 'PositionsPage',
  setup() {
    const positions = ref([])
    const loading = ref(false)
    const error = ref(null)
    const showModal = ref(false)
    const positionDetails = ref(null)

    const filters = ref({
      symbol: '',
      exchange: '',
      productType: '',
      netQty: ''
    })

    const filteredPositions = computed(() => {
      let result = [...positions.value]

      // Filter by symbol
      if (filters.value.symbol) {
        const symbolLower = filters.value.symbol.toLowerCase()
        result = result.filter(position =>
          (position.tradingsymbol || position.symbolname || '').toLowerCase().includes(symbolLower)
        )
      }

      // Filter by exchange
      if (filters.value.exchange) {
        result = result.filter(position =>
          position.exchange === filters.value.exchange
        )
      }

      // Filter by product type
      if (filters.value.productType) {
        result = result.filter(position =>
          position.producttype === filters.value.productType
        )
      }

      // Filter by net qty
      if (filters.value.netQty) {
        const netQty = parseFloat(filters.value.netQty)
        if (filters.value.netQty === 'positive') {
          result = result.filter(position => parseFloat(position.netqty || 0) > 0)
        } else if (filters.value.netQty === 'negative') {
          result = result.filter(position => parseFloat(position.netqty || 0) < 0)
        } else if (filters.value.netQty === 'zero') {
          result = result.filter(position => parseFloat(position.netqty || 0) === 0)
        }
      }

      return result
    })

    const hasActiveFilters = computed(() => {
      return !!(
        filters.value.symbol ||
        filters.value.exchange ||
        filters.value.productType ||
        filters.value.netQty
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

    const formatNetValue = (netValue) => {
      if (!netValue) return '₹0.00'
      // Handle negative values with "- " prefix
      const valueStr = String(netValue).trim()
      if (valueStr.startsWith('-')) {
        const numValue = parseFloat(valueStr.replace('- ', '').replace('-', ''))
        return `-₹${formatPrice(numValue)}`
      }
      const numValue = parseFloat(valueStr)
      if (isNaN(numValue)) return '₹0.00'
      return `₹${formatPrice(numValue)}`
    }

    const calculateTotalNetValue = () => {
      return filteredPositions.value.reduce((sum, pos) => {
        const valueStr = String(pos.netvalue || '0').trim()
        const isNegative = valueStr.startsWith('-')
        const value = parseFloat(valueStr.replace('- ', '').replace('-', ''))
        return sum + (isNegative ? -value : value)
      }, 0)
    }

    const fetchPositions = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await apiClient.get('/positions')
        
        if (response.data && response.data.status && response.data.data) {
          positions.value = Array.isArray(response.data.data) ? response.data.data : []
        } else if (Array.isArray(response.data)) {
          positions.value = response.data
        } else {
          positions.value = []
        }
      } catch (err) {
        console.error('Failed to fetch positions:', err)
        error.value = err.response?.data?.detail || err.message || 'Failed to fetch positions'
        positions.value = []
      } finally {
        loading.value = false
      }
    }

    const refreshPositions = () => {
      fetchPositions()
    }

    const clearFilters = () => {
      filters.value = {
        symbol: '',
        exchange: '',
        productType: '',
        netQty: ''
      }
    }

    const openPositionDetails = (position) => {
      positionDetails.value = position
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      positionDetails.value = null
    }

    onMounted(() => {
      fetchPositions()
    })

    return {
      positions,
      loading,
      error,
      filters,
      filteredPositions,
      hasActiveFilters,
      formatPrice,
      formatNetValue,
      calculateTotalNetValue,
      refreshPositions,
      clearFilters,
      showModal,
      positionDetails,
      openPositionDetails,
      closeModal
    }
  }
}
</script>
