import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests if available
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('sessionToken')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  } else {
    console.warn('No session token found in localStorage')
  }
  return config
})

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sessionToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

