<template>
  <div id="app" class="min-h-screen bg-gray-50 dark:bg-dark-900">
    <Navigation v-if="showNavigation" />
    <router-view />
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navigation from './components/Navigation.vue'

export default {
  name: 'App',
  components: {
    Navigation
  },
  setup() {
    const route = useRoute()
    
    // Show navigation on all pages except login, register, and app selector
    const showNavigation = computed(() => {
      const noNavRoutes = ['/login', '/register', '/apps']
      return !noNavRoutes.includes(route.path)
    })
    
    return {
      showNavigation
    }
  }
}
</script>

