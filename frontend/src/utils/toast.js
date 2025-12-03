/**
 * Toast notification utility using Flowbite
 */

/**
 * Show a success toast notification
 * @param {string} message - The message to display
 */
export function showSuccess(message) {
  const toast = createToast('success', message)
  document.body.appendChild(toast)
  triggerToast(toast)
}

/**
 * Show an error toast notification
 * @param {string} message - The message to display
 */
export function showError(message) {
  const toast = createToast('error', message)
  document.body.appendChild(toast)
  triggerToast(toast)
}

/**
 * Show an info toast notification
 * @param {string} message - The message to display
 */
export function showInfo(message) {
  const toast = createToast('info', message)
  document.body.appendChild(toast)
  triggerToast(toast)
}

/**
 * Show a warning toast notification
 * @param {string} message - The message to display
 */
export function showWarning(message) {
  const toast = createToast('warning', message)
  document.body.appendChild(toast)
  triggerToast(toast)
}

/**
 * Create a toast element
 * @param {string} type - Toast type (success, error, info, warning)
 * @param {string} message - The message to display
 * @returns {HTMLElement} Toast element
 */
function createToast(type, message) {
  const toastId = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
  
  const icons = {
    success: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>`,
    error: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path></svg>`,
    info: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"></path></svg>`,
    warning: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path></svg>`
  }
  
  const colors = {
    success: 'text-success-600 bg-success-50 dark:bg-success-900 dark:text-success-200',
    error: 'text-danger-600 bg-danger-50 dark:bg-danger-900 dark:text-danger-200',
    info: 'text-primary-600 bg-primary-50 dark:bg-primary-900 dark:text-primary-200',
    warning: 'text-accent-600 bg-accent-50 dark:bg-accent-900 dark:text-accent-200'
  }
  
  const toast = document.createElement('div')
  toast.id = toastId
  toast.className = `fixed top-4 right-4 z-50 flex items-center w-full max-w-xs p-4 mb-4 ${colors[type]} rounded-lg shadow-lg transition-all duration-300 transform translate-x-full opacity-0`
  toast.setAttribute('role', 'alert')
  
  toast.innerHTML = `
    <div class="inline-flex items-center justify-center flex-shrink-0 w-8 h-8 rounded-lg">
      ${icons[type]}
    </div>
    <div class="ml-3 text-sm font-normal">${message}</div>
    <button type="button" class="ml-auto -mx-1.5 -my-1.5 ${colors[type]} rounded-lg focus:ring-2 focus:ring-gray-300 p-1.5 inline-flex h-8 w-8 items-center justify-center hover:bg-opacity-20 dark:hover:bg-opacity-30" data-dismiss-target="#${toastId}" aria-label="Close">
      <span class="sr-only">Close</span>
      <svg class="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
        <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
      </svg>
    </button>
  `
  
  // Add close button functionality
  const closeButton = toast.querySelector('[data-dismiss-target]')
  closeButton.addEventListener('click', () => {
    removeToast(toast)
  })
  
  return toast
}

/**
 * Trigger the toast animation
 * @param {HTMLElement} toast - Toast element
 */
function triggerToast(toast) {
  // Trigger animation
  setTimeout(() => {
    toast.classList.remove('translate-x-full', 'opacity-0')
    toast.classList.add('translate-x-0', 'opacity-100')
  }, 10)
  
  // Auto remove after 5 seconds
  setTimeout(() => {
    removeToast(toast)
  }, 5000)
}

/**
 * Remove toast with animation
 * @param {HTMLElement} toast - Toast element
 */
function removeToast(toast) {
  toast.classList.add('translate-x-full', 'opacity-0')
  setTimeout(() => {
    if (toast.parentNode) {
      toast.parentNode.removeChild(toast)
    }
  }, 300)
}

