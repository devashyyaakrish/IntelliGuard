/**
 * WebSocket Service — Real-time feed connection management
 */

class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectDelay = 2000
    this.maxRetries = 10
    this.retryCount = 0
    this.url = `${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/feed`
  }

  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return

    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      this.retryCount = 0
      this._emit('connection', { status: 'connected' })
    }

    this.ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)
        this._emit(message.type, message.data)
        this._emit('any', message)
      } catch (e) {
        console.error('WS parse error:', e)
      }
    }

    this.ws.onclose = () => {
      this._emit('connection', { status: 'disconnected' })
      this._reconnect()
    }

    this.ws.onerror = (err) => {
      this._emit('connection', { status: 'error', error: err })
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.onclose = null
      this.ws.close()
      this.ws = null
    }
  }

  on(eventType, callback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set())
    }
    this.listeners.get(eventType).add(callback)
    return () => this.off(eventType, callback)
  }

  off(eventType, callback) {
    this.listeners.get(eventType)?.delete(callback)
  }

  _emit(eventType, data) {
    this.listeners.get(eventType)?.forEach((cb) => {
      try { cb(data) } catch (e) { console.error('Listener error:', e) }
    })
  }

  _reconnect() {
    if (this.retryCount >= this.maxRetries) return
    this.retryCount++
    const delay = this.reconnectDelay * Math.min(this.retryCount, 5)
    setTimeout(() => this.connect(), delay)
  }

  get isConnected() {
    return this.ws?.readyState === WebSocket.OPEN
  }
}

export const wsService = new WebSocketService()
