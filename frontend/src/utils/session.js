/**
 * Session utility functions for accessing SmartAPI session data
 */

/**
 * Get the current SmartAPI session from store or localStorage
 * @returns {Object|null} Session object with access_token, feed_token, etc.
 */
export function getSession() {
  try {
    // Try to get from localStorage first (persists across page reloads)
    const stored = localStorage.getItem('smartapiSession')
    if (stored) {
      return JSON.parse(stored)
    }
  } catch (e) {
    console.error('Error reading session from localStorage:', e)
  }
  return null
}

/**
 * Get the access token for API calls
 * @returns {string|null} Access token or null if not available
 */
export function getAccessToken() {
  const session = getSession()
  return session?.access_token || null
}

/**
 * Get the feed token for WebSocket connections
 * @returns {string|null} Feed token or null if not available
 */
export function getFeedToken() {
  const session = getSession()
  return session?.feed_token || null
}

/**
 * Check if session is valid (not expired)
 * @returns {boolean} True if session exists and is not expired
 */
export function isSessionValid() {
  const session = getSession()
  if (!session || !session.token_expiry) {
    return false
  }
  
  const expiry = new Date(session.token_expiry)
  const now = new Date()
  return expiry > now
}

/**
 * Get the active app ID from session
 * @returns {number|null} App ID or null if not available
 */
export function getActiveAppId() {
  const session = getSession()
  return session?.app_id || null
}

