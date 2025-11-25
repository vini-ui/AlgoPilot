<template>
  <div class="min-h-screen bg-gray-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex justify-between items-center mb-6">
        <h1 class="text-3xl font-bold text-gray-900">App Selector</h1>
        <button
          @click="showAddModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Add New App
        </button>
      </div>

      <div v-if="loading" class="text-center py-12">
        <p class="text-gray-500">Loading apps...</p>
      </div>

      <div v-else-if="apps.length === 0" class="text-center py-12">
        <p class="text-gray-500 mb-4">No apps configured yet.</p>
        <button
          @click="showAddModal = true"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Add Your First App
        </button>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="app in apps"
          :key="app.id"
          class="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
        >
          <div class="flex justify-between items-start mb-4">
            <h3 class="text-xl font-semibold text-gray-900">{{ app.name }}</h3>
            <span
              :class="[
                'px-2 py-1 text-xs rounded-full',
                app.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              ]"
            >
              {{ app.status }}
            </span>
          </div>
          
          <p class="text-gray-600 mb-4">Account: {{ app.account_id }}</p>
          
          <div class="flex items-center mb-4">
            <input
              :id="`default-${app.id}`"
              type="checkbox"
              :checked="app.is_default"
              @change="toggleDefault(app.id)"
              class="mr-2"
            />
            <label :for="`default-${app.id}`" class="text-sm text-gray-700">
              Make Default
            </label>
          </div>
          
          <div class="flex gap-2">
            <button
              @click="switchApp(app.id)"
              class="flex-1 bg-blue-600 text-white px-3 py-2 rounded-md text-sm hover:bg-blue-700"
            >
              Switch to App
            </button>
            <button
              @click="editApp(app)"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm hover:bg-gray-50"
            >
              Edit
            </button>
            <button
              @click="deleteApp(app.id)"
              class="px-3 py-2 border border-red-300 text-red-600 rounded-md text-sm hover:bg-red-50"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddModal || editingApp"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 class="text-2xl font-bold mb-4">
          {{ editingApp ? 'Edit App' : 'Add New App' }}
        </h2>
        <form @submit.prevent="saveApp" class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              App Name
            </label>
            <input
              v-model="formData.name"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Account ID
            </label>
            <input
              v-model="formData.account_id"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div class="flex gap-2">
            <button
              type="submit"
              class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
            >
              Save
            </button>
            <button
              type="button"
              @click="closeModal"
              class="flex-1 bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../store/app'
import apiClient from '../api/client'

export default {
  name: 'AppSelectorPage',
  setup() {
    const router = useRouter()
    const appStore = useAppStore()
    const loading = ref(false)
    const showAddModal = ref(false)
    const editingApp = ref(null)
    const formData = ref({
      name: '',
      account_id: ''
    })

    const apps = computed(() => appStore.apps)

    const loadApps = async () => {
      loading.value = true
      try {
        const response = await apiClient.get('/apps')
        appStore.setApps(response.data)
      } catch (error) {
        console.error('Failed to load apps:', error)
      } finally {
        loading.value = false
      }
    }

    const switchApp = async (appId) => {
      try {
        await apiClient.post(`/apps/${appId}/switch`)
        await loadApps()
        router.push('/dashboard')
      } catch (error) {
        console.error('Failed to switch app:', error)
      }
    }

    const toggleDefault = async (appId) => {
      try {
        await apiClient.post(`/apps/${appId}/set-default`)
        await loadApps()
      } catch (error) {
        console.error('Failed to set default:', error)
      }
    }

    const editApp = (app) => {
      editingApp.value = app
      formData.value = {
        name: app.name,
        account_id: app.account_id
      }
    }

    const deleteApp = async (appId) => {
      if (!confirm('Are you sure you want to delete this app?')) return
      
      try {
        await apiClient.delete(`/apps/${appId}`)
        appStore.removeApp(appId)
      } catch (error) {
        console.error('Failed to delete app:', error)
      }
    }

    const saveApp = async () => {
      try {
        if (editingApp.value) {
          await apiClient.put(`/apps/${editingApp.value.id}`, formData.value)
        } else {
          await apiClient.post('/apps', formData.value)
        }
        await loadApps()
        closeModal()
      } catch (error) {
        console.error('Failed to save app:', error)
      }
    }

    const closeModal = () => {
      showAddModal.value = false
      editingApp.value = null
      formData.value = { name: '', account_id: '' }
    }

    onMounted(() => {
      loadApps()
    })

    return {
      apps,
      loading,
      showAddModal,
      editingApp,
      formData,
      switchApp,
      toggleDefault,
      editApp,
      deleteApp,
      saveApp,
      closeModal
    }
  }
}
</script>

