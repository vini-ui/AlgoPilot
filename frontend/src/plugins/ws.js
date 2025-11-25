export class WSMessage {
  constructor(data) {
    Object.assign(this, data)
  }
}

class WebSocketClient {
  constructor() {
    this.ws = null
    this.url = ''
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 3000
  }

  connect(token) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = import.meta.env.VITE_WS_HOST || 'localhost:8000'
    this.url = `${protocol}//${host}/ws/live?token=${token}`

    try {
      this.ws = new WebSocket(this.url)
      this.setupHandlers()
    } catch (error) {
      console.error('WebSocket connection error:', error)
      this.attemptReconnect(token)
    }
  }

  setupHandlers() {
    if (!this.ws) return

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      // Attempt to reconnect if not manually closed
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnect(this.url.split('token=')[1])
      }
    }
  }

  attemptReconnect(token) {
    this.reconnectAttempts++
    setTimeout(() => {
      console.log(`Reconnecting... (attempt ${this.reconnectAttempts})`)
      this.connect(token)
    }, this.reconnectDelay)
  }

  onMessage(callback) {
    if (this.ws) {
      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          callback(message)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

export const wsClient = new WebSocketClient()

