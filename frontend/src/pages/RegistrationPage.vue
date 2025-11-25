<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
      <h1 class="text-3xl font-bold text-gray-800 mb-2">Create Account</h1>
      <p class="text-gray-600 mb-6">Sign up for AlgoPilot</p>
      
      <form @submit.prevent="handleRegister" class="space-y-4">
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
            placeholder="Choose a username"
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
            minlength="6"
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Enter a password (min 6 characters)"
          />
        </div>
        
        <div>
          <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-1">
            Confirm Password
          </label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            required
            class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Confirm your password"
          />
        </div>
        
        <button
          type="submit"
          :disabled="loading || password !== confirmPassword"
          class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {{ loading ? 'Creating account...' : 'Register' }}
        </button>
      </form>
      
      <p v-if="password && confirmPassword && password !== confirmPassword" class="mt-2 text-sm text-red-600">
        Passwords do not match
      </p>
      
      <p v-if="error" class="mt-4 text-sm text-red-600">{{ error }}</p>
      
      <p v-if="success" class="mt-4 text-sm text-green-600">{{ success }}</p>
      
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Already have an account?
          <router-link to="/login" class="text-blue-600 hover:text-blue-700 font-medium">
            Login here
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import apiClient from '../api/client'

export default {
  name: 'RegistrationPage',
  setup() {
    const router = useRouter()
    const username = ref('')
    const password = ref('')
    const confirmPassword = ref('')
    const loading = ref(false)
    const error = ref('')
    const success = ref('')

    const handleRegister = async () => {
      if (password.value !== confirmPassword.value) {
        error.value = 'Passwords do not match'
        return
      }

      if (password.value.length < 6) {
        error.value = 'Password must be at least 6 characters long'
        return
      }

      loading.value = true
      error.value = ''
      success.value = ''
      
      try {
        await apiClient.post('/register', {
          username: username.value,
          password: password.value
        })
        
        success.value = 'Account created successfully! Redirecting to login...'
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/login')
        }, 2000)
      } catch (err) {
        error.value = err?.response?.data?.detail || 'Registration failed. Please try again.'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      confirmPassword,
      loading,
      error,
      success,
      handleRegister
    }
  }
}
</script>

