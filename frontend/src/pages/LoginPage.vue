<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">AlgoPilot</h1>
      <p class="text-gray-600 mb-6">Trading Automation Platform</p>
      
      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label for="username" class="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            id="username"
            v-model="username"
            type="text"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your username"
          />
        </div>
        
        <div>
          <label for="password" class="block text-sm font-medium text-gray-700 mb-1">
            Master Password / PIN
          </label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter your password"
          />
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
      
      <p v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</p>
      
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Don't have an account?
          <router-link to="/register" class="text-blue-600 hover:text-blue-700 font-medium">
            Register here
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'
import apiClient from '../api/client'

export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const username = ref('vineysharmaui@outlook.com')
    const password = ref('Active@2020')
    const loading = ref(false)
    const error = ref('')

    const handleLogin = async () => {
      loading.value = true
      error.value = ''
      
      try {
        const response = await apiClient.post('/login', {
          username: username.value,
          password: password.value
        })
        
        // Handle both 'token' and 'access_token' from response
        const token = response.data.token || response.data.access_token
        const user = response.data.user
        
        if (!token) {
          error.value = 'No token received from server'
          return
        }
        
        authStore.login(token, user)
        localStorage.setItem('sessionToken', token)
        
        router.push('/apps')
      } catch (err) {
        error.value = err?.response?.data?.detail || 'Login failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      loading,
      error,
      handleLogin
    }
  }
}
</script>

